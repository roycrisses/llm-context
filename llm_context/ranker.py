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
_CAMEL_RE = re.compile(r"([a-z])([A-Z])")


def _tokenize(text: str) -> List[str]:
    """
    Extract lowercase alphanumeric tokens from *text*.
    Splits on punctuation, whitespace, and underscores intelligently.
    """
    # Use findall on original text to preserve case for camelCase detection
    raw = _TOKEN_RE.findall(text)
    expanded: List[str] = []
    for tok in raw:
        # Split camelCase / snake_case into sub-tokens if needed
        has_underscore = "_" in tok
        if has_underscore or (not tok.islower() and not tok.isupper()):
            # Split on camelCase then replace underscores with spaces
            s = _CAMEL_RE.sub(r"\1 \2", tok)
            if has_underscore:
                s = s.replace("_", " ")
            parts = s.split()
            if len(parts) > 1:
                for p in parts:
                    expanded.append(p.lower())

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
    """
    n_docs = len(files)
    if n_docs == 0:
        return []

    query_set = set(query_terms)

    # Tokenize documents and build sets for DF calculation
    doc_tokens: List[List[str]] = []
    doc_sets: List[set[str]] = []
    for f in files:
        tokens = _tokenize(f["rel_path"] + " " + f["content"])
        doc_tokens.append(tokens)
        doc_sets.append(set(tokens))

    # Document frequency for query terms only
    df: dict[str, int] = {}
    for term in query_terms:
        count = sum(1 for s in doc_sets if term in s)
        df[term] = count

    # Pre-calculate IDF values
    idfs: dict[str, float] = {}
    for term in query_terms:
        idfs[term] = math.log((n_docs + 1) / (df[term] + 1)) + 1.0

    scores: List[float] = []
    for tokens in doc_tokens:
        doc_len = max(len(tokens), 1)
        # Only count TF for terms that are in the query
        local_tf: dict[str, int] = {}
        for t in tokens:
            if t in query_set:
                local_tf[t] = local_tf.get(t, 0) + 1

        score = 0.0
        for term, count in local_tf.items():
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
    now = time.time()

    scored: List[tuple[float, int]] = []
    for idx, (f, base_score) in enumerate(zip(files, tfidf_scores)):
        # Inline recency boost for performance
        age = now - f["mtime"]
        if age < 0:
            recency = 0.10
        elif age >= _RECENCY_WINDOW_SECONDS:
            recency = 0.0
        else:
            recency = 0.10 * (1.0 - age / _RECENCY_WINDOW_SECONDS)

        total = (
            base_score
            + _filename_boost(f["rel_path"], query_terms)
            + recency
        )
        scored.append((total, idx))

    # Sort descending by score, then ascending by path for stability
    scored.sort(key=lambda x: (-x[0], files[x[1]]["rel_path"]))

    return [files[idx] for _, idx in scored]
