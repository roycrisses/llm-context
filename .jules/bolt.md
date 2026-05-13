## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2025-05-16 - Single-Pass TF-IDF and Memory Pressure
**Learning:** In codebases with many large files, storing all tokens for all documents in memory (`doc_tokens`, `doc_sets`) creates massive memory overhead and increases garbage collection pressure. By counting term frequencies (TF) for query terms *only* during tokenization, we can skip storing the full token lists, reducing memory from O(N * L) to O(N * Q).
**Action:** Avoid storing full tokenization results in memory; count and discard tokens in a single pass when possible.
