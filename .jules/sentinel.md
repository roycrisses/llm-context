## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-18 - Enhanced Sensitive File Exclusions in Scanner
**Vulnerability:** The scanner was including sensitive files like .env.staging, SSH private keys (id_rsa), and database backups (.sql, .dump) if they were not explicitly in .gitignore.
**Learning:** Default exclusion lists should be aggressive for security-sensitive artifacts in tools that send codebase context to external APIs.
**Prevention:** Use prefix-based checks for .env files to catch all environment variations and include a broad set of sensitive extensions and common credential filenames in default exclusions.
