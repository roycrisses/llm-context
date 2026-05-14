## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2025-05-20 - Dictionary Allocation Overhead in Ranking
**Learning:** Building a full term-frequency dictionary (`dict[str, int]`) for every file during ranking is expensive when only a few query terms are relevant. Iterating over the token list once and summing pre-calculated IDFs for query terms is ~2x faster and significantly reduces memory churn.
**Action:** Avoid constructing intermediate frequency maps for scoring when the set of relevant terms is small and fixed.
