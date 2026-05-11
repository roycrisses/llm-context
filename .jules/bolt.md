## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2025-05-22 - Caching tiktoken Encoder Lookups
**Learning:** Repeatedly attempting to `import tiktoken` in a function called within a tight loop (like `count_tokens` during file truncation) causes a massive performance degradation (~150x) when the library is not installed. Python's import machinery has significant overhead for failed imports that are repeatedly retried.
**Action:** Always use `@functools.lru_cache` or a global flag to cache the result of expensive/repeated import attempts or library lookups in performance-critical paths.
