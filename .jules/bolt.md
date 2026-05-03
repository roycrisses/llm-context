## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2026-05-03 - Tiktoken Encoder Caching
**Learning:** Calling `tiktoken.get_encoding` repeatedly (e.g., in a loop over file lines) is surprisingly expensive because it often triggers a local import and an internal registry lookup. Caching the encoder object with `functools.lru_cache` significantly reduces this overhead.
**Action:** Always cache tiktoken encoder objects when they are used for repeated token counting operations.
