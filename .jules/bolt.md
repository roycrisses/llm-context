# Bolt's Journal - Critical Learnings

## 2025-05-14 - Optimized TF-IDF Ranking
**Learning:** The previous TF-IDF implementation was O(Terms * Docs * Tokens) because it re-scanned every document's tokens for each query term to calculate Document Frequency. Refactoring to a single-pass O(Docs * Tokens) approach, combined with pre-calculating IDF, improved performance by ~3x (from 2.76s to 0.95s for 1000 documents).
**Action:** Always prefer single-pass collection of statistics (TF, DF) when processing large sets of documents.

## 2025-05-14 - Tokenization Bottleneck
**Learning:** `re.sub` and `re.findall` in a loop over all tokens in a codebase can be significant. By checking for uppercase or underscores before attempting to split camelCase/snake_case, we can skip expensive regex for the majority of simple tokens.
**Action:** Use fast early-out checks (like `isupper()` or `in`) to avoid expensive operations on paths that don't need them.
