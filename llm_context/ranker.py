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
    # Use findall on raw text to preserve casing for camelCase detection
    raw = _TOKEN_RE.findall(text)
    expanded: List[str] = []
    for tok in raw:
        # Fast path: skip regex if no uppercase or underscores (cannot be camelCase/snake_case)
        # Most tokens in source code are already lowercase or simple words.
        if tok.islower() and "_" not in tok:
            expanded.append(tok)
            continue

        # Also split camelCase into sub-tokens
        # Use a check to avoid expensive re.sub if no lowercase-uppercase transition exists
        if any(c.isupper() for c in tok):
            parts = re.sub(r"([a-z])([A-Z])", r"\1 \2", tok).split()
            if len(parts) > 1:
                expanded.extend(p.lower() for p in parts)

        # Split on underscores for snake_case
        if "_" in tok:
            parts = tok.split("_")
            expanded.extend(p.lower() for p in parts if p)

        expanded.append(tok.lower())
    return expanded


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
    2. Compute document frequency for each query term across all docs using sets.
    3. Pre-calculate IDF for each query term.
    4. Score each doc as the sum of ``tf * idf`` for every query term.
    """
    n_docs = len(files)
    if n_docs == 0:
        return []

    # Tokenize documents (path + content)
    doc_tokens: List[List[str]] = []
    # Create sets for faster DF calculation
    doc_token_sets: List[set[str]] = []

    for f in files:
        combined = f["rel_path"] + " " + f["content"]
        tokens = _tokenize(combined)
        doc_tokens.append(tokens)
        doc_token_sets.append(set(tokens))

    # Document frequency for query terms only using hash lookups
    df: dict[str, int] = {}
    for term in query_terms:
        count = 0
        for token_set in doc_token_sets:
            if term in token_set:
                count += 1
        df[term] = count

    # Pre-calculate IDF values for query terms
    idf_map: dict[str, float] = {}
    for term in query_terms:
        # Smoothed IDF
        idf_map[term] = math.log((n_docs + 1) / (df.get(term, 0) + 1)) + 1.0

    scores: List[float] = []
    query_set = set(query_terms)
    for tokens in doc_tokens:
        # Optimization: Only count frequency of query terms
        tf_counts: dict[str, int] = {}
        for tok in tokens:
            if tok in query_set:
                tf_counts[tok] = tf_counts.get(tok, 0) + 1

        doc_len = max(len(tokens), 1)
        score = 0.0
        for term in query_terms:
            raw_tf = tf_counts.get(term, 0)
            if raw_tf == 0:
                continue
            # Normalised TF * Pre-calculated IDF
            score += (raw_tf / doc_len) * idf_map[term]
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

    # Capture a single timestamp to ensure stable ranking across multiple files
    now = time.time()

    scored: List[tuple[float, int]] = []
    for idx, (f, base_score) in enumerate(zip(files, tfidf_scores)):
        # Inline recency boost calculation using the stable 'now' timestamp
        age = now - f["mtime"]
        r_boost = 0.0
        if age < 0:
            r_boost = 0.10
        elif age < _RECENCY_WINDOW_SECONDS:
            r_boost = 0.10 * (1.0 - age / _RECENCY_WINDOW_SECONDS)

        total = (
            base_score
            + _filename_boost(f["rel_path"], query_terms)
            + r_boost
        )
        scored.append((total, idx))

    # Sort descending by score, then ascending by path for stability
    scored.sort(key=lambda x: (-x[0], files[x[1]]["rel_path"]))

    return [files[idx] for _, idx in scored]
