## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2025-05-16 - Tokenizer Encoder Caching
**Learning:** Initializing or looking up a `tiktoken` encoder via `get_encoding` involves registry lookups that add significant overhead when called repeatedly. More importantly, if `tiktoken` is NOT installed, every call to `import tiktoken` inside a function triggers a costly failed import attempt. Caching the encoder (or the `None` result) using `lru_cache` provides an ~115x-150x speedup in environments without the library.
**Action:** Always cache library-specific encoder lookups and avoid repeated imports in high-frequency loops.
