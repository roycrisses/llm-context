"""
trimmer.py — Token counting and smart trimming so context fits inside any
LLM's token budget.

Token limits per model (conservative, to leave room for the answer):
  gpt-4o   → 120,000
  gpt-4    →   8,000
  claude   → 180,000
  gemini   → 900,000
  ollama   →   4,000

Uses tiktoken when available; falls back to the chars / 4 heuristic.
"""

from __future__ import annotations

from typing import List, Optional

from llm_context.scanner import FileInfo


# ---------------------------------------------------------------------------
# Token limits
# ---------------------------------------------------------------------------

MODEL_TOKEN_LIMITS: dict[str, int] = {
    "gpt-4o": 120_000,
    "gpt-4": 8_000,
    "claude": 180_000,
    "gemini": 900_000,
    "ollama": 4_000,
}

_DEFAULT_MODEL = "gpt-4o"
# Tokens reserved for the context header/footer and the model's answer
_OVERHEAD_TOKENS = 512


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------


def _get_tiktoken_encoder(model: str):
    """
    Return a tiktoken encoder for *model*, or None if tiktoken is not
    installed or the model is not supported.
    """
    try:
        import tiktoken

        # Map our model names → tiktoken encoding names
        encoding_map = {
            "gpt-4o": "cl100k_base",
            "gpt-4": "cl100k_base",
        }
        encoding_name = encoding_map.get(model, "cl100k_base")
        return tiktoken.get_encoding(encoding_name)
    except Exception:
        return None


def count_tokens(text: str, model: str = _DEFAULT_MODEL) -> int:
    """
    Count the number of tokens in *text* for the given *model*.

    Uses tiktoken when available (accurate); falls back to
    ``len(text) // 4`` (fast estimate). Empty strings always return 0.

    Parameters
    ----------
    text:
        The string to measure.
    model:
        One of the supported model keys (e.g. ``"gpt-4o"``).

    Returns
    -------
    int
        Estimated token count.
    """
    if not text:
        return 0

    enc = _get_tiktoken_encoder(model)
    if enc is not None:
        try:
            return len(enc.encode(text))
        except Exception:
            pass
    # Fallback: 1 token ≈ 4 characters (commonly cited rule of thumb)
    return max(1, len(text) // 4)


def get_token_limit(model: str) -> int:
    """
    Return the maximum output token budget for *model*.

    Unrecognised model names fall back to the ``gpt-4o`` limit.

    Parameters
    ----------
    model:
        Model key string (case-insensitive lookup).

    Returns
    -------
    int
        Token budget in tokens.
    """
    return MODEL_TOKEN_LIMITS.get(model.lower(), MODEL_TOKEN_LIMITS[_DEFAULT_MODEL])


# ---------------------------------------------------------------------------
# Smart per-file truncation
# ---------------------------------------------------------------------------


def _truncate_file_content(
    content: str,
    max_tokens: int,
    model: str,
    head_lines: int = 60,
) -> str:
    """
    If *content* exceeds *max_tokens*, return the first *head_lines* lines
    followed by a truncation notice.  This keeps the most-relevant (top)
    portion of the file.

    Parameters
    ----------
    content:
        Full file content.
    max_tokens:
        Token budget available for this file's content.
    model:
        Model key for token counting.
    head_lines:
        Number of leading lines to keep when truncation is needed.

    Returns
    -------
    str
        Original or truncated content.
    """
    if count_tokens(content, model) <= max_tokens:
        return content

    lines = content.splitlines()
    kept: List[str] = []
    used = 0
    for line in lines:
        line_tokens = count_tokens(line, model) + 1  # +1 for newline
        if used + line_tokens > max_tokens:
            break
        kept.append(line)
        used += line_tokens

    # Ensure we kept at least the first head_lines lines regardless
    if len(kept) < min(head_lines, len(lines)):
        kept = lines[:head_lines]

    truncation_note = f"\n# ... [{len(lines) - len(kept)} lines truncated to fit token budget] ..."
    return "\n".join(kept) + truncation_note


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def trim_to_budget(
    files: List[FileInfo],
    model: str = _DEFAULT_MODEL,
    max_tokens: Optional[int] = None,
    header_tokens: int = _OVERHEAD_TOKENS,
) -> List[FileInfo]:
    """
    Select as many ranked files as possible within the token budget, and
    trim any individual file that is too large to fit in full.

    Files are consumed in order (highest-ranked first).  For each file:

    1. If there is no budget left, stop.
    2. If the file fits, include it as-is.
    3. If the file is too large, truncate it to however many tokens remain
       and include the trimmed version.

    Parameters
    ----------
    files:
        Pre-ranked list of :class:`~llm_context.scanner.FileInfo` dicts
        (most relevant first).
    model:
        Model key used to look up the default token limit and for counting.
    max_tokens:
        Override the model's default token limit.
    header_tokens:
        Tokens to reserve for the context header/footer.

    Returns
    -------
    List[FileInfo]
        A (possibly smaller and/or content-trimmed) list of FileInfo dicts
        that fit within the budget.  Contents of trimmed files are updated
        in-place on copies of the originals.
    """
    budget = max_tokens if max_tokens is not None else get_token_limit(model)
    budget = max(0, budget - header_tokens)

    result: List[FileInfo] = []
    remaining = budget

    for f in files:
        if remaining <= 0:
            break

        # Wrap content in code-fence, as it appears in the final output
        wrapped = f"```{f['extension']}\n{f['content']}\n```"
        file_tokens = count_tokens(wrapped, model)

        if file_tokens <= remaining:
            result.append(f)
            remaining -= file_tokens
        else:
            # Try to fit a truncated version
            if remaining > 50:  # Only worth including if meaningful space remains
                trimmed_content = _truncate_file_content(
                    f["content"],
                    remaining - 20,
                    model,  # -20 for fence overhead
                )
                # Make a shallow copy with updated content and truncation status
                is_truncated = trimmed_content != f["content"]
                trimmed_file: FileInfo = {**f, "content": trimmed_content, "truncated": is_truncated}
                result.append(trimmed_file)
            remaining = 0  # Budget exhausted after forced truncation

    return result
