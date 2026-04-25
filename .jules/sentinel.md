## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-25 - Prevent Leakage of Secrets, SSH Keys, and Environment Files
**Vulnerability:** The scanner was including sensitive files like private SSH keys (`id_rsa`), SSL certificates (`.pem`, `.crt`), and arbitrary environment files (e.g., `.env.production`).
**Learning:** A "deny-by-filename" approach for secrets is often incomplete. Environment files and cryptographic keys frequently use common extensions or prefixes that can be blocked systematically.
**Prevention:** Use prefix-based matching for `.env*` files (except `.env.example`) and maintain a comprehensive list of sensitive extensions (`.pem`, `.key`, `.gpg`, etc.) and filenames (`id_rsa`, `.npmrc`) to prevent accidental inclusion in LLM context.
