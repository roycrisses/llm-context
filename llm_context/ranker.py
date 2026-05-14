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
    # 1. Expand camelCase: "getUserName" -> "get User Name"
    # Done before lowercasing so we can detect uppercase boundaries
    expanded = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    # 2. Treat underscores as delimiters: "get_user" -> "get user"
    expanded = expanded.replace("_", " ")

    # 3. Find all alphanumeric tokens
    raw = _TOKEN_RE.findall(expanded.lower())

    # 4. Include the original tokens if they were split
    # (Re-matching on original text to get original tokens)
    original_tokens = _TOKEN_RE.findall(text.lower())

    # Using a list to preserve duplicates (important for TF)
    return raw + original_tokens


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

    Strategy
    --------
    1. Build a per-file token list from ``rel_path + content``.
    2. Compute document frequency for each query term across all docs.
    3. Score each doc as the sum of ``tf * idf`` for every query term.
    """
    n_docs = len(files)
    if n_docs == 0:
        return []

    query_terms_set = set(query_terms)
    df: dict[str, int] = {term: 0 for term in query_terms}
    doc_tokens_list: List[List[str]] = []

    # Optimization: Tokenize and compute Document Frequency (DF) in a single pass
    for f in files:
        tokens = _tokenize(f["rel_path"] + " " + f["content"])
        doc_tokens_list.append(tokens)

        # Count each query term at most once per document for DF
        doc_set = set(tokens)
        for term in query_terms_set:
            if term in doc_set:
                df[term] += 1

    # Pre-calculate IDFs for query terms
    idfs: dict[str, float] = {
        term: math.log((n_docs + 1) / (df[term] + 1)) + 1.0 for term in query_terms
    }

    # Score each document: iterate tokens once and sum IDFs of matches
    # Mathematically equivalent to (count / doc_len) * idf summed over query terms
    scores: List[float] = []
    for tokens in doc_tokens_list:
        doc_len = max(len(tokens), 1)
        score = sum(idfs[t] for t in tokens if t in idfs)
        scores.append(score / doc_len)

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

    scored: List[tuple[float, int]] = []
    now = time.time()  # Capture once for all recency boosts
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
