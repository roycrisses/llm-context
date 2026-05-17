## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-14 - Insufficient Secret File Exclusions in Scanner
**Vulnerability:** The scanner failed to exclude common sensitive files such as SSH private keys (e.g., `id_rsa`), certificates/keys (e.g., `.pem`), and environment files with suffixes (e.g., `.env.test`). These files often contain plaintext secrets.
**Learning:** Hardcoded exclusion lists must be comprehensive and account for common naming conventions for secrets and credentials. Matching only exact `.env` names is insufficient as developers often use environment-specific suffixes.
**Prevention:** Implement a broad exclusion list for sensitive file extensions (.pem, .key, .gpg) and patterns (id_rsa*, .env*). Use prefix matching for `.env` files while allowing safe examples like `.env.example`.
