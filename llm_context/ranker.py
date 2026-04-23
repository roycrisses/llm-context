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
from typing import List, Optional

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
    # Performance: don't lower() the whole text upfront to allow camelCase detection
    raw = _TOKEN_RE.findall(text)
    expanded: List[str] = []
    for tok in raw:
        # Performance optimization: skip regex for simple lowercase tokens without underscores
        if tok.islower() and "_" not in tok:
            expanded.append(tok)
            continue

        # Also split camelCase and handle underscores
        tok_split = re.sub(r"([a-z])([A-Z])", r"\1 \2", tok).replace("_", " ")
        parts = tok_split.split()

        for p in parts:
            p_low = p.lower()
            expanded.append(p_low)

        tok_low = tok.lower()
        if tok_low not in expanded:
            expanded.append(tok_low)

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

    Strategy
    --------
    1. Build a per-file token list from ``rel_path + content``.
    2. Compute document frequency for each query term across all docs.
    3. Score each doc as the sum of ``tf * idf`` for every query term.
    """
    n_docs = len(files)
    if n_docs == 0:
        return []

    # Tokenize documents (path + content) and compute DF in one pass for efficiency
    doc_tokens_list: List[List[str]] = []
    df: dict[str, int] = {term: 0 for term in query_terms}
    query_terms_set = set(query_terms)

    for f in files:
        combined = f["rel_path"] + " " + f["content"]
        tokens = _tokenize(combined)
        doc_tokens_list.append(tokens)

        unique_tokens = set(tokens)
        for term in query_terms_set:
            if term in unique_tokens:
                df[term] += 1

    # Pre-calculate IDF for query terms
    idf_map: dict[str, float] = {}
    for term in query_terms:
        # Smoothed IDF
        idf_map[term] = math.log((n_docs + 1) / (df[term] + 1)) + 1.0

    scores: List[float] = []
    for tokens in doc_tokens_list:
        doc_len = max(len(tokens), 1)

        # Count frequencies for query terms only
        tf_counts: dict[str, int] = {}
        for tok in tokens:
            if tok in query_terms_set:
                tf_counts[tok] = tf_counts.get(tok, 0) + 1

        score = 0.0
        for term, count in tf_counts.items():
            # Normalised TF
            normalised_tf = count / doc_len
            score += normalised_tf * idf_map[term]
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
    stem = os.path.splitext(os.path.basename(rel_path))[0]
    stem_tokens = _tokenize(stem)
    hits = sum(1 for t in query_terms if t in stem_tokens)
    return 0.15 * hits


def _recency_boost(mtime: float, now: Optional[float] = None) -> float:
    """
    Return a small additive boost for files modified within the last week.
    Boost decays linearly from 0.10 → 0.0 over the recency window.
    """
    if now is None:
        now = time.time()

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

    # Performance: capture time once for the whole loop
    now = time.time()
    scored: List[tuple[float, int]] = []
    for idx, (f, base_score) in enumerate(zip(files, tfidf_scores)):
        total = (
            base_score
            + _filename_boost(f["rel_path"], query_terms)
            + _recency_boost(f["mtime"], now=now)
        )
        scored.append((total, idx))

    # Sort descending by score, then ascending by path for stability
    scored.sort(key=lambda x: (-x[0], files[x[1]]["rel_path"]))

    return [files[idx] for _, idx in scored]
