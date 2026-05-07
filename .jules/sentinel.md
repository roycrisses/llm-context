## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-21 - Expanded Sensitive File Exclusions
**Vulnerability:** The scanner was not excluding common sensitive file types like private keys (.pem, .key), certificates, and various .env variants (e.g., .env.staging). These could be accidentally sent to an LLM, leaking credentials.
**Learning:** Hardcoding a list of specific .env files is brittle. Using a prefix match for `.env*` while specifically allowing `.env.example` is more robust and secure.
**Prevention:** Maintain a comprehensive list of sensitive extensions and use pattern matching for environment files to catch variants automatically.
