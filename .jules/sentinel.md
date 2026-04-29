## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-12 - Expanded Secret and Credential Exclusions
**Vulnerability:** The scanner only excluded exactly `.env`, leaving variants like `.env.staging` or `.env.local` potentially exposed. It also missed common credential formats like `.pem` and `.npmrc`.
**Learning:** For LLM context tools, a "deny-by-default" approach for everything starting with `.env` (except `.env.example`) is safer than trying to list all possible environment file suffixes.
**Prevention:** Use prefix matching for sensitive file patterns (e.g., `.env*`) and maintain a comprehensive list of credential-bearing extensions (`.pem`, `.key`, `.p12`) and specific config files (`.npmrc`, `.netrc`).
