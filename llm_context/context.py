"""
context.py — Assembles the final, formatted context block from a list of
trimmed FileInfo dicts and the user's query metadata.
"""

from __future__ import annotations

from typing import List

from llm_context.scanner import FileInfo
from llm_context.trimmer import count_tokens, get_token_limit


# ---------------------------------------------------------------------------
# Block assembly
# ---------------------------------------------------------------------------

_DIVIDER = "---"


def build_context_block(
    files: List[FileInfo],
    query: str,
    model: str = "gpt-4o",
    max_tokens: int | None = None,
) -> str:
    """
    Assemble and return the full context block string ready to be sent to
    an LLM or copied to the clipboard.

    Output format
    -------------
    ::

        ---
        CODEBASE CONTEXT
        Question: <query>
        Model: <model> | Token budget: <limit> | Files included: <n>
        ---
        ### relative/path/to/file.py
        ```py
        <content>
        ```
        ---
        (repeated for each file)
        ---
        END OF CONTEXT. Answer the question: <query>
        ---

    Parameters
    ----------
    files:
        Trimmed list of :class:`~llm_context.scanner.FileInfo` dicts
        (as returned by :func:`~llm_context.trimmer.trim_to_budget`).
    query:
        The user's natural-language question.
    model:
        Model key string used to look up the token budget for the header.
    max_tokens:
        Override the model's default token limit (shown in the header).

    Returns
    -------
    str
        The fully-formatted context block.

    Raises
    ------
    ValueError
        When *query* is empty or *files* is empty.
    """
    if not query or not query.strip():
        raise ValueError("Query must be a non-empty string.")
    if not files:
        raise ValueError(
            "No files to include in the context block. "
            "Check that the directory contains readable source files."
        )

    token_budget = max_tokens if max_tokens is not None else get_token_limit(model)

    parts: List[str] = []

    # ── Header ──────────────────────────────────────────────────────────────
    parts.append(_DIVIDER)
    parts.append("CODEBASE CONTEXT")
    parts.append(f"Question: {query}")
    parts.append(f"Model: {model} | Token budget: {token_budget:,} | Files included: {len(files)}")
    parts.append(_DIVIDER)

    # ── File blocks ─────────────────────────────────────────────────────────
    for f in files:
        ext = f["extension"] or "txt"
        parts.append(f"### {f['rel_path']}")
        parts.append(f"```{ext}")
        parts.append(f["content"])
        parts.append("```")
        parts.append(_DIVIDER)

    # ── Footer ──────────────────────────────────────────────────────────────
    parts.append(f"END OF CONTEXT. Answer the question: {query}")
    parts.append(_DIVIDER)

    return "\n".join(parts)


def context_token_count(block: str, model: str = "gpt-4o") -> int:
    """
    Return the token count of an assembled context block.

    Parameters
    ----------
    block:
        The string produced by :func:`build_context_block`.
    model:
        Model key used for token counting.

    Returns
    -------
    int
        Estimated total token count.
    """
    return count_tokens(block, model)
