## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.
## 2025-05-21 - Memory-Efficient TF-IDF Ranking
**Learning:** Storing full token lists and sets for every document during ranking creates a massive memory bottleneck (O(TotalTokens)) and leads to redundant iterations. A single-pass approach that only tracks query term frequencies and document frequencies significantly reduces memory pressure and improves speed.
**Action:** Always process large datasets (like codebase tokens) in a single pass whenever possible to minimize memory footprint.
