## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-21 - Robust Environment File and Sensitive Artifact Exclusions
**Vulnerability:** The scanner used a fixed list of common `.env` filenames, which could miss environment-specific files like `.env.production.local`. It also lacked exclusions for SSH keys and SSL certificates.
**Learning:** Enumerating sensitive files is an uphill battle. A hybrid approach of broad prefix matching (for `.env*`) combined with a robust list of common sensitive extensions (`.pem`, `.key`, `.pub`) and filenames (`id_rsa`, `.npmrc`) provides better defense-in-depth.
**Prevention:** Use `filename.startswith(".env")` while explicitly allowing `.env.example`. Maintain a comprehensive `frozenset` of sensitive extensions and filenames that should never be sent to an LLM.
