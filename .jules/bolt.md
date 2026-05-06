## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2025-05-16 - Single-Pass TF-IDF and Token Pre-filtering
**Learning:** In TF-IDF ranking, pre-filtering document tokens against the query set before computing term frequencies (TF) drastically reduces memory usage and avoids unnecessary dictionary lookups for non-relevant terms. Combining TF and DF calculations into a single pass over tokens further minimizes iteration overhead.
**Action:** Always pre-filter tokens when the query is known, and use `collections.Counter` for efficient counting.
