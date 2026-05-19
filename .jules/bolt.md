## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2026-05-19 - Caching tiktoken Encoders
**Learning:** Python's `import` system does not cache failed attempts (`ImportError`). In a codebase that performs repeated token counting (e.g., during file trimming), calling a function that tries to import `tiktoken` on every invocation results in massive overhead if the library is missing (~500x slower in benchmarks).
**Action:** Use `functools.lru_cache` to cache the results of optional dependency lookups and encoder initialization to ensure near-zero overhead on repeated calls.
