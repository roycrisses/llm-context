## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2026-05-07 - Optimized Token Counting and Test Resilience
**Learning:** In environments where `tiktoken` might not be installed, repeated `import tiktoken` calls and encoder lookups in a loop create significant overhead. Using `functools.lru_cache` on the encoder lookup function drastically reduces this overhead. Additionally, when testing token budgets, ensure `max_tokens` accounts for hardcoded overhead constants (like `_OVERHEAD_TOKENS`) to prevent unexpected empty results.
**Action:** Always cache expensive library-loading or initialization functions, and use realistic token budgets in tests that exceed internal overheads.
