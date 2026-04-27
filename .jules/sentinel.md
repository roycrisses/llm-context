## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-27 - Hardening Against Credentials Leakage and DoS via Special Files
**Vulnerability:** The scanner could potentially include sensitive credentials (SSH keys, auth tokens, .env variations) and attempt to read non-regular files (FIFOs, sockets), leading to data leakage or DoS.
**Learning:** Broad exclusion patterns (like `.env*`) are safer than enumerating specific environment files. Using `Path.is_file()` is essential to avoid hanging on special Unix files during recursive directory walks.
**Prevention:** Use prefix-based matching for sensitive file patterns. Always verify that a path refers to a regular file before attempting to read its content in a generic scanner.
