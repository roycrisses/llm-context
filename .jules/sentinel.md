## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-21 - Fix Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was including sensitive files like SSH keys, credentials, and database backups in the context sent to LLMs. It was also including various `.env` variants (e.g., `.env.staging`).
**Learning:** Hardcoded exclusion lists need to be comprehensive to cover common developer secrets. Relying only on a few patterns like `.env` is insufficient.
**Prevention:** Implement defense-in-depth by excluding broad categories of sensitive files by name (`id_rsa`, `.npmrc`) and extension (`.pem`, `.sql`, `.bak`). Specifically filter all `.env` files except explicitly safe ones like `.env.example`.
