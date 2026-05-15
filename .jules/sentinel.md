## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-15 - Enhance Scanner to Exclude Secrets and Sensitive Files
**Vulnerability:** The scanner was including sensitive files like `.env.staging`, `.npmrc`, and SSH private keys in the LLM context.
**Learning:** A static list of `.env` files is insufficient. Many developers use variants like `.env.local` or `.env.staging` which should also be excluded. Additionally, SSH keys and other credential files must be proactively blocked.
**Prevention:** Use prefix-based matching for `.env` files (excluding `.env.example`). Maintain an extensive list of common sensitive file extensions (e.g., `.pem`, `.key`) and filenames (e.g., `id_rsa`, `.npmrc`) to ensure they never leak into LLM prompts.
