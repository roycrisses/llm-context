## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2026-05-05 - Counter and Pre-filtering for TF-IDF
**Learning:** Using `collections.Counter` with a generator expression that pre-filters tokens against a query set is significantly faster (approx. 60% faster) than building a full frequency dictionary and then looking up query terms. It reduces dictionary insertions and lookups from O(Total Tokens) to O(Query-related Tokens).
**Action:** Always pre-filter tokens when counting frequencies if only a small subset of terms (like query terms) is needed.
