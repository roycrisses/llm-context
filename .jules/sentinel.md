## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.
## 2026-05-22 - Prevent Sensitive File Leakage in Scanner
**Vulnerability:** The scanner was including sensitive files like .env.staging, .npmrc, and SSH private keys in the LLM context.
**Learning:** Default exclusion lists must be aggressive and include common secret patterns and configuration files that may contain tokens.
**Prevention:** Maintain a comprehensive list of sensitive extensions and filenames, and use prefix matching for .env files to catch environment variations.
