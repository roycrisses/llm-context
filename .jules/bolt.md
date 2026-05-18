## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2025-05-16 - Tokenizer Encoder Caching
**Learning:** Python does not cache failed imports. Repeatedly attempting to import a missing library (like `tiktoken`) in a tight loop can be extremely costly (~200x slower in benchmarks). Caching the result of the import attempt using `lru_cache` ensures the penalty is only paid once.
**Action:** Always cache the results of optional dependency checks and expensive resource lookups that occur in frequently called functions.
