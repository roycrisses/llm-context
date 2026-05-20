## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-20 - Broadening Sensitive File Exclusions
**Vulnerability:** The scanner was including various sensitive files like specialized `.env.*` files (e.g., `.env.secret`), SSH private keys (e.g., `id_rsa`), and database dumps (e.g., `.sql`, `.bak`), which could leak credentials when sent to an LLM.
**Learning:** Hardcoded lists of sensitive files are often incomplete. A combination of suffix-based checks (for `.env*`), common filename lists, and extension-based exclusions provides a more robust defense in depth.
**Prevention:** Use `filename.startswith(".env")` to catch all environment variations while allowing `.env.example`. Maintain an expansive list of security-related extensions (`.pem`, `.key`, `.crt`) and common secret filenames.
