## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2026-05-16 - Caching 'tiktoken' Encoders
**Learning:** Repeatedly attempting to import an unavailable library in a tight loop can incur significant overhead (up to ~100ms for 1000 calls). Additionally, looking up encoders by model name repeatedly is redundant.
**Action:** Use `@functools.lru_cache` for encoder lookups to ensure that the import cost and lookup logic are only paid once per model.
