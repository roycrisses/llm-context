"""
cli.py — Click-based command-line interface for llm-context.

Usage
-----
    llm-context ./my-project --ask "why is auth broken?"
    llm-context ./my-project --ask "explain models" --model claude --send
    llm-context ./my-project --ask "refactor async" --copy
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from llm_context.context import build_context_block, context_token_count
from llm_context.ranker import rank_files
from llm_context.scanner import scan_directory
from llm_context.trimmer import MODEL_TOKEN_LIMITS, get_token_limit, trim_to_budget


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _echo_error(msg: str) -> None:
    click.echo(click.style(f"Error: {msg}", fg="red"), err=True)


def _echo_info(msg: str) -> None:
    click.echo(click.style(msg, fg="cyan"), err=True)


def _echo_success(msg: str) -> None:
    click.echo(click.style(msg, fg="green"), err=True)


def _plural(count: int, word: str) -> str:
    """Simple pluralization helper."""
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "directory",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--ask",
    "-q",
    required=True,
    help="Your question about the codebase.",
    metavar="QUESTION",
)
@click.option(
    "--model",
    "-m",
    default="gpt-4o",
    show_default=True,
    type=click.Choice(list(MODEL_TOKEN_LIMITS.keys()), case_sensitive=False),
    help="Target LLM model (controls token budget).",
)
@click.option(
    "--send",
    "do_send",
    is_flag=True,
    default=False,
    help="Send the context directly to the LLM and print the response.",
)
@click.option(
    "--copy",
    "do_copy",
    is_flag=True,
    default=False,
    help="Copy the context block to the clipboard.",
)
@click.option(
    "--max-tokens",
    default=None,
    type=int,
    help="Override the default token limit for the chosen model.",
    metavar="N",
)
@click.option(
    "--include",
    default=None,
    multiple=True,
    help="Glob pattern of files to force-include (repeatable).",
    metavar="GLOB",
)
@click.option(
    "--exclude",
    default=None,
    multiple=True,
    help="Glob pattern of files to force-exclude (repeatable).",
    metavar="GLOB",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    help="Save context to a file instead of printing to stdout.",
    metavar="FILE",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Print scan/rank progress information to stderr.",
)
def main(
    directory: Path,
    ask: str,
    model: str,
    do_send: bool,
    do_copy: bool,
    max_tokens: Optional[int],
    include: tuple[str, ...],
    exclude: tuple[str, ...],
    output: Optional[Path],
    verbose: bool,
) -> None:
    """
    Analyze DIRECTORY, find files relevant to your --ask question, and
    assemble a ready-to-use LLM context block.

    \b
    Examples
    --------
      llm-context ./my-project --ask "why is auth broken?"
      llm-context ./src --ask "explain the data models" --model gpt-4 --send
      llm-context . --ask "refactor to async" --model claude --copy
    """
    model = model.lower()
    extra_includes = list(include) if include else None
    extra_excludes = list(exclude) if exclude else None

    # ── 1. Scan ─────────────────────────────────────────────────────────────
    if verbose:
        _echo_info(f"🔍 Scanning '{directory}' …")

    try:
        files = scan_directory(
            directory,
            extra_includes=extra_includes,
            extra_excludes=extra_excludes,
        )
    except (FileNotFoundError, NotADirectoryError) as exc:
        _echo_error(str(exc))
        sys.exit(1)

    if not files:
        _echo_error(
            f"No readable source files found in '{directory}'. "
            "Check your --include / --exclude flags."
        )
        sys.exit(1)

    if verbose:
        _echo_info(f"✅ Found {_plural(len(files), 'file')}.")

    # ── 2. Rank ─────────────────────────────────────────────────────────────
    if verbose:
        _echo_info("🎯 Ranking files by relevance …")

    try:
        ranked = rank_files(files, ask)
    except ValueError as exc:
        _echo_error(str(exc))
        sys.exit(1)

    # ── 3. Trim ─────────────────────────────────────────────────────────────
    if verbose:
        token_limit = max_tokens or get_token_limit(model)
        _echo_info(f"✂️ Trimming to {token_limit:,} token budget …")

    trimmed = trim_to_budget(ranked, model=model, max_tokens=max_tokens)

    if not trimmed:
        _echo_error("Token budget is too small to include even one file.")
        sys.exit(1)

    if verbose:
        _echo_info(f"📦 Including {_plural(len(trimmed), 'file')} in context.")

    # ── 4. Assemble ─────────────────────────────────────────────────────────
    try:
        context_block = build_context_block(trimmed, query=ask, model=model, max_tokens=max_tokens)
    except ValueError as exc:
        _echo_error(str(exc))
        sys.exit(1)

    # ── 5. Output ───────────────────────────────────────────────────────────
    tokens = context_token_count(context_block, model=model)

    num_included = len(trimmed)
    num_truncated = sum(1 for f in trimmed if f.get("truncated"))
    num_omitted = len(files) - num_included

    # Build detail string: " (1 truncated, 2 omitted)"
    details = []
    if num_truncated:
        details.append(f"{num_truncated} truncated")
    if num_omitted:
        details.append(f"{num_omitted} omitted")
    detail_str = f" ({', '.join(details)})" if details else ""

    summary = f"✨ Included {_plural(num_included, 'file')}{detail_str} ({tokens:,} tokens)."

    if output:
        try:
            output.write_text(context_block, encoding="utf-8")
            _echo_success(f"💾 Context saved to '{output}'. {summary}")
        except OSError as exc:
            _echo_error(f"Could not write to '{output}': {exc}")
            sys.exit(1)
    elif not do_send:
        # Default: print to stdout
        click.echo(context_block)
        _echo_info(summary)

    if do_copy:
        try:
            import pyperclip  # type: ignore

            pyperclip.copy(context_block)
            _echo_success(f"📋 Context copied to clipboard. {summary}")
        except ImportError:
            _echo_error("pyperclip is not installed. Install with: pip install pyperclip")
        except Exception as exc:
            _echo_error(f"Clipboard copy failed: {exc}")

    # ── 6. Send ─────────────────────────────────────────────────────────────
    if do_send:
        _echo_info(f"🚀 Sending context to '{model}' …")

        try:
            from llm_context.llm import send

            response = send(context_block, model=model)
        except (EnvironmentError, ImportError, ConnectionError, ValueError) as exc:
            _echo_error(str(exc))
            sys.exit(1)

        click.echo(response)
