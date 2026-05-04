## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2026-05-04 - Caching Token Encoders
**Learning:** `tiktoken.get_encoding` and similar lookups can be surprisingly slow when called repeatedly in a loop, especially if they involve `try-import` blocks for optional dependencies. Caching the encoder object (or the failure to load it) using `@lru_cache` provides a massive speedup (~150x in this case) for a very low complexity cost.
**Action:** Always cache expensive resource lookups or optional dependency checks that are used in hot paths like token counting.
