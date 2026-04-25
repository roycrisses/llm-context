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
    # Find tokens BEFORE lowercasing to preserve camelCase for splitting
    raw = _TOKEN_RE.findall(text)
    expanded: List[str] = []
    for tok in raw:
        # Optimization: skip complex regex splitting for simple lowercase tokens
        # Check if it has any uppercase letters or underscores before trying to split
        has_upper = any(c.isupper() for c in tok)
        has_underscore = "_" in tok

        if has_upper or has_underscore:
            # Handle camelCase
            processed = re.sub(r"([a-z])([A-Z])", r"\1 \2", tok) if has_upper else tok
            # Handle snake_case by replacing underscores with spaces for .split()
            if "_" in processed:
                processed = processed.replace("_", " ")

            parts = processed.split()
            # Only add sub-tokens if we actually split something (e.g. "User" -> "User")
            if len(parts) > 1:
                for p in parts:
                    expanded.append(p.lower())

        # Always include the original token (lowercased)
        expanded.append(tok.lower())
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

    Optimization: Tokenization, TF, and DF are computed in a single pass
    to avoid multiple traversals of the document collection.
    """
    n_docs = len(files)
    if n_docs == 0:
        return []

    query_terms_set = set(query_terms)
    df: dict[str, int] = {}
    doc_data: List[tuple[dict[str, float], int]] = []

    # Single pass: tokenize, compute TF for query terms, and track DF
    for f in files:
        combined = f["rel_path"] + " " + f["content"]
        tokens = _tokenize(combined)
        doc_len = max(len(tokens), 1)

        # We only care about TF for query terms
        tf: dict[str, float] = {}
        unique_terms_in_doc = set()

        for tok in tokens:
            if tok in query_terms_set:
                tf[tok] = tf.get(tok, 0) + 1
                if tok not in unique_terms_in_doc:
                    df[tok] = df.get(tok, 0) + 1
                    unique_terms_in_doc.add(tok)

        doc_data.append((tf, doc_len))

    # Pre-calculate IDF for query terms
    idf_map: dict[str, float] = {}
    for term in query_terms:
        # Smoothed IDF
        idf_map[term] = math.log((n_docs + 1) / (df.get(term, 0) + 1)) + 1.0

    scores: List[float] = []
    for tf, doc_len in doc_data:
        score = 0.0
        for term, count in tf.items():
            # Normalised TF * Pre-calculated IDF
            score += (count / doc_len) * idf_map[term]
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
