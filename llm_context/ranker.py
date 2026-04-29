"""
ranker.py — Scores each file by relevance to the user's query using
TF-IDF keyword matching, with bonus boosts for filename matches and
recently modified files.
"""

from __future__ import annotations

import math
import os
import re
import time
from typing import List

from llm_context.scanner import FileInfo


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


def _tokenize(text: str) -> List[str]:
    """
    Extract lowercase alphanumeric tokens from *text*.
    Splits on punctuation, whitespace, and underscores intelligently.
    """
    # Find tokens first without lowercasing to preserve camelCase for splitting
    raw = _TOKEN_RE.findall(text)
    expanded: List[str] = []
    for tok in raw:
        lowered = tok.lower()
        # Only split if it looks like snake_case or camelCase
        if "_" in tok or (tok != lowered and not tok.isupper()):
            parts = re.sub(r"([a-z])([A-Z])", r"\1 \2", tok.replace("_", " ")).split()
            for p in parts:
                pl = p.lower()
                if pl != lowered:
                    expanded.append(pl)
        expanded.append(lowered)
    return expanded


def _term_frequency(tokens: List[str]) -> dict[str, float]:
    """Return a dict of term → raw count for *tokens*."""
    tf: dict[str, float] = {}
    for tok in tokens:
        tf[tok] = tf.get(tok, 0) + 1
    return tf


# ---------------------------------------------------------------------------
# TF-IDF scorer
# ---------------------------------------------------------------------------


def _compute_tfidf_scores(
    files: List[FileInfo],
    query_terms: List[str],
) -> List[float]:
    """
    Compute a single TF-IDF relevance score for each file against the
    user's query terms.
    """
    n_docs = len(files)
    if n_docs == 0:
        return []

    query_term_set = set(query_terms)
    df: dict[str, int] = {term: 0 for term in query_terms}
    doc_tfs: List[dict[str, float]] = []
    doc_lens: List[int] = []

    for f in files:
        tokens = _tokenize(f["rel_path"] + " " + f["content"])
        tf = _term_frequency(tokens)
        doc_tfs.append(tf)
        doc_lens.append(max(len(tokens), 1))

        # Use set intersection to find which query terms are present
        for term in (query_term_set & tf.keys()):
            df[term] += 1

    idfs: dict[str, float] = {
        term: math.log((n_docs + 1) / (df[term] + 1)) + 1.0 for term in query_terms
    }

    scores: List[float] = []
    for tf, doc_len in zip(doc_tfs, doc_lens):
        score = 0.0
        # Only iterate over query terms that are actually in this document
        for term in (query_term_set & tf.keys()):
            score += (tf[term] / doc_len) * idfs[term]
        scores.append(score)

    return scores


# ---------------------------------------------------------------------------
# Boost helpers
# ---------------------------------------------------------------------------

_RECENCY_WINDOW_SECONDS = 7 * 24 * 3600  # 1 week


def _filename_boost(rel_path: str, query_terms: List[str]) -> float:
    """
    Return a small additive boost when the file name contains one or more
    query keywords.  Prioritises exact stem matches.
    """
    stem = os.path.splitext(os.path.basename(rel_path))[0].lower()
    stem_tokens = _tokenize(stem)
    hits = sum(1 for t in query_terms if t in stem_tokens)
    return 0.15 * hits


def _recency_boost(mtime: float, now: float) -> float:
    """
    Return a small additive boost for files modified within the last week.
    Boost decays linearly from 0.10 → 0.0 over the recency window.
    """
    age = now - mtime
    if age < 0:
        return 0.10
    if age >= _RECENCY_WINDOW_SECONDS:
        return 0.0
    return 0.10 * (1.0 - age / _RECENCY_WINDOW_SECONDS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def rank_files(files: List[FileInfo], query: str) -> List[FileInfo]:
    """
    Score and sort *files* by their relevance to *query*.

    Scoring combines:
    - **TF-IDF** cosine-like similarity of file content + path vs query
    - **Filename boost** when the file basename contains query keywords
    - **Recency boost** for files modified within the last 7 days

    Parameters
    ----------
    files:
        List of :class:`~llm_context.scanner.FileInfo` dicts as returned
        by :func:`~llm_context.scanner.scan_directory`.
    query:
        The natural-language question from the user.

    Returns
    -------
    List[FileInfo]
        The same list, re-ordered from most relevant to least relevant.
        Files with a zero score (no keyword overlap at all) are placed at
        the end but still included so nothing is silently dropped.

    Raises
    ------
    ValueError
        When *query* is empty.
    """
    if not query or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    if not files:
        return []

    query_terms = list(set(_tokenize(query)))

    tfidf_scores = _compute_tfidf_scores(files, query_terms)
    now = time.time()

    scored: List[tuple[float, int]] = []
    for idx, (f, base_score) in enumerate(zip(files, tfidf_scores)):
        total = (
            base_score
            + _filename_boost(f["rel_path"], query_terms)
            + _recency_boost(f["mtime"], now)
        )
        scored.append((total, idx))

    # Sort descending by score, then ascending by path for stability
    scored.sort(key=lambda x: (-x[0], files[x[1]]["rel_path"]))

    return [files[idx] for _, idx in scored]
