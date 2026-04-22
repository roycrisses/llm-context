## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-22 - Prevent Sensitive Data Leaks via Scanner Exclusion and DoS via Non-Regular Files
**Vulnerability:** The scanner was not excluding common sensitive files like SSH keys, authentication configurations, and various `.env` file patterns. It was also not skipping non-regular files (like FIFOs or sockets), which could cause the scanner to hang, leading to a Denial of Service (DoS) during codebase analysis.
**Learning:** A codebase context tool must proactively blacklist a wide range of sensitive artifacts to prevent accidental exposure to LLMs. Relying on a minimal list like `.env` is insufficient. Furthermore, using `pathlib.Path.is_file()` is essential to ensure only regular files are processed, avoiding potential DoS from blocking on special files.
**Prevention:** Maintain a comprehensive and evolving list of excluded sensitive filenames and extensions. Always use `is_file()` (which returns `False` for FIFOs/sockets/etc.) and `is_symlink()` to safely traverse directories.
