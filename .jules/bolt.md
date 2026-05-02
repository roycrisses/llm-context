## 2025-05-15 - TF-IDF Optimization and Tokenization
**Learning:** Document Frequency (DF) calculation was previously O(Q * N * L), where Q is query terms, N is number of files, and L is average file length. By pre-calculating token sets for each document, DF calculation becomes O(Q * N), which is significantly faster for large codebases. Additionally, processing string replacements and regex expansions on the full text *before* tokenization is much more efficient than doing it per-token in a loop.
**Action:** Use sets for document existence checks and perform bulk string operations outside of tight token loops.

## 2025-05-22 - Directory Traversal and Gitignore Pruning
**Learning:** `os.walk` descends into all subdirectories by default. Even if files are later ignored by `.gitignore`, the overhead of visiting every file in a directory like `node_modules` or `dist` is massive (O(Files) complexity). Pruning the `dirnames` list in-place during `os.walk` prevents this descent, reducing complexity to O(Qualifying Paths).
**Action:** Always prune `dirnames` in `os.walk` for known-ignored directories (including those from `.gitignore`) unless force-includes are requested.

## 2025-05-22 - Redundant Metadata Calls
**Learning:** Each `Path.stat()` or `os.stat()` call is a system call. In a tight directory traversal loop, calling `stat()` multiple times for the same file (once to check size, once for mtime, etc.) adds up. Passing already-retrieved metadata to child functions avoids these redundant calls.
**Action:** Pass `stat` objects or specific attributes (like `size`) into helper functions to minimize system calls.
