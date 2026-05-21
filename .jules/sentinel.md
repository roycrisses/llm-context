## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-21 - Enhanced Sensitive File Exclusions
**Vulnerability:** Accidental inclusion of sensitive files (SSH keys, .env variations, database backups) in the LLM context.
**Learning:** Default exclusions should be broad and proactive, covering common sensitive file types like .pem, .sql, and all .env variations except .env.example.
**Prevention:** Maintain comprehensive _EXCLUDED_FILENAMES and _EXCLUDED_EXTENSIONS lists. Use prefix-based checks for patterns like .env to catch local/staging variants.
