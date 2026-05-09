## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2026-05-09 - Tiktoken Caching and Filename Boost Optimization
**Learning:** Initializing or retrieving tiktoken encoders can be expensive due to vocabulary loading. Caching the encoder with `lru_cache` provides a significant speedup when `count_tokens` is called repeatedly (e.g., during trimming). Additionally, converting stem tokens to a set in `_filename_boost` ensures O(1) lookups for query terms, which is more efficient than repeated list scanning.
**Action:** Always cache expensive resource lookups (like LLM encoders) and use sets for membership checks in hot paths.
