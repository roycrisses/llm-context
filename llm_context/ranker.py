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
    1. Tokenize each file once, counting only keywords from the query.
    2. Compute document frequency (DF) and IDFs for query terms.
    3. Score each doc using normalized TF * IDF.
    """
    n_docs = len(files)
    if n_docs == 0:
        return []

    # Optimization: single-pass tokenization to collect TF and DF simultaneously.
    # This avoids storing full token lists for every document in memory.
    df: dict[str, int] = {term: 0 for term in query_terms}
    doc_stats: List[tuple[int, dict[str, int]]] = []

    for f in files:
        tokens = _tokenize(f["rel_path"] + " " + f["content"])
        doc_len = len(tokens)

        # Only count frequencies for terms present in the query
        counts: dict[str, int] = {}
        found_in_doc = set()

        for tok in tokens:
            if tok in df: # O(1) lookup in query term dict
                counts[tok] = counts.get(tok, 0) + 1
                if tok not in found_in_doc:
                    df[tok] += 1
                    found_in_doc.add(tok)

        doc_stats.append((max(doc_len, 1), counts))

    # Pre-calculate IDFs for query terms
    idfs: dict[str, float] = {}
    for term in query_terms:
        # Smoothed IDF: log((N+1)/(DF+1)) + 1
        idfs[term] = math.log((n_docs + 1) / (df[term] + 1)) + 1.0

    # Score each document
    scores: List[float] = []
    for doc_len, counts in doc_stats:
        score = 0.0
        for term, count in counts.items():
            # Normalised TF * Pre-calculated IDF
            score += (count / doc_len) * idfs[term]
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
    # Optimization: use a set for O(1) keyword lookups
    stem_tokens = set(_tokenize(stem))
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
