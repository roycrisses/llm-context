## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-21 - Expanded Sensitive File and Environment Variable Exclusion
**Vulnerability:** The scanner only excluded a specific subset of `.env` files and missed many sensitive file types like SSH keys, certificates, and package manager config files (e.g., `.npmrc`). This could lead to accidental leakage of secrets when users provide repository context to an LLM.
**Learning:** Hardcoded lists of sensitive files are often incomplete. A "deny-all" approach for patterns like `.env*` (with specific safe exceptions like `.env.example`) is more robust than listing individual environment files.
**Prevention:** Implement broad prefix matching for sensitive patterns (like `.env*`) and maintain an extensive list of common sensitive extensions (`.pem`, `.key`, `.crt`, etc.) and filenames to ensure secrets are not included in the LLM context.
