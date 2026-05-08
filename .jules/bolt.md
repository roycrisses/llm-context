## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2025-05-15 - Regex-based Gitignore and Directory Pruning
**Learning:** In codebases with large .gitignore files, calling fnmatch for every file/pattern combination is a massive bottleneck (O(N*M)). Pre-compiling patterns into a combined regex and using it for early directory pruning in os.walk provides a 6x+ speedup by skipping entire ignored trees and reducing syscalls.
**Action:** Always prefer combined regexes over repeated glob matching in hot loops, and prune directory traversal as early as possible.
