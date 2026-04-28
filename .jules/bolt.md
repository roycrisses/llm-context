## 2025-05-15 - TF-IDF Ranking Optimization

**Learning:** The original TF-IDF implementation had O(Q * N * L) complexity for Document Frequency (DF) calculation because it iterated over every token of every document for every query term. Additionally, tokenization was inefficient and buggy, lowercasing text before attempting camelCase splitting and performing expensive regex on every token.

**Action:**
1. Use `set` intersection for DF and TF scoring to reduce complexity to O(N * L + Q * N).
2. Optimize `_tokenize` by skipping regex for purely lowercase/uppercase tokens and splitting before lowercasing to preserve camelCase.
3. Hoist syscalls like `time.time()` out of loops to reduce overhead.
