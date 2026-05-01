## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-21 - Prevent Leakage of Credentials and Environment Files
**Vulnerability:** The scanner was leaking sensitive credentials, SSH private keys (e.g., `id_rsa`), and non-standard environment files (e.g., `.env.staging`, `.env.local`) because the exclusion list was too narrow.
**Learning:** Prefix-based matching (e.g., `startswith(".env")`) is significantly more robust than exact filename matching for sensitive configuration files. Including common security extensions (.pem, .key, .crt) by default provides defense-in-depth for context-gathering tools.
**Prevention:** Use pattern matching for sensitive file categories and maintain a comprehensive, documented list of "forbidden" extensions and filenames that should never be included in an LLM context block.
