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
    raw = _TOKEN_RE.findall(text)
    expanded: List[str] = []
    for tok in raw:
        # Optimization: skip complex regex if token is already simple lowercase
        # (most common case during large content scans)
        if tok.islower() and "_" not in tok:
            expanded.append(tok)
            continue

        # Also split camelCase / snake_case into sub-tokens
        # We do this before lowercasing to catch camelCase
        parts = re.sub(r"([a-z])([A-Z])", r"\1 \2", tok).replace("_", " ").split()
        expanded.extend(p.lower() for p in parts)
        expanded.append(tok.lower())
    return expanded


def _term_frequency(tokens: List[str], query_terms: List[str] | None = None) -> dict[str, float]:
    """
    Return a dict of term → raw count for *tokens*.
    If *query_terms* is provided, only counts those terms (faster).
    """
    tf: dict[str, float] = {}
    if query_terms:
        q_set = set(query_terms)
        for tok in tokens:
            if tok in q_set:
                tf[tok] = tf.get(tok, 0) + 1
    else:
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

    # Tokenize documents (path + content) and track document frequency for query terms
    # Optimization: Combined tokenization, set creation, and DF counting into a single pass
    doc_tokens: List[List[str]] = []
    df: dict[str, int] = {term: 0 for term in query_terms}
    query_set = set(query_terms)

    for f in files:
        combined = f["rel_path"] + " " + f["content"]
        tokens = _tokenize(combined)
        doc_tokens.append(tokens)

        # Count DF for query terms present in this document
        found_in_doc = query_set.intersection(tokens)
        for term in found_in_doc:
            df[term] += 1

    # Pre-calculate IDF values for each query term
    # Optimization: Calculate IDF once per term instead of per doc-term
    idfs: dict[str, float] = {}
    for term in query_terms:
        # Smoothed IDF
        idfs[term] = math.log((n_docs + 1) / (df.get(term, 0) + 1)) + 1.0

    scores: List[float] = []
    for tokens in doc_tokens:
        # Optimization: Only count TF for terms that actually appear in the query
        tf = _term_frequency(tokens, query_terms)
        doc_len = max(len(tokens), 1)
        score = 0.0
        for term, raw_tf in tf.items():
            # Normalised TF
            normalised_tf = raw_tf / doc_len
            score += normalised_tf * idfs[term]
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


def _recency_boost(mtime: float, now: float | None = None) -> float:
    """
    Return a small additive boost for files modified within the last week.
    Boost decays linearly from 0.10 → 0.0 over the recency window.
    """
    reference_time = now if now is not None else time.time()
    age = reference_time - mtime
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

    # Optimization: capture time once for all recency checks
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
