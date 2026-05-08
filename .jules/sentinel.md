## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2025-05-15 - Comprehensive Sensitive File Exclusions
**Vulnerability:** The scanner only excluded a small set of hardcoded `.env` filenames, leaving other variations (like `.env.staging`) and other sensitive files (SSH keys, `.npmrc`, certificates) exposed to being sent to LLMs.
**Learning:** Relying on exact filename matches for security-sensitive files is brittle. Prefix-based matching for environment files and a broad list of sensitive extensions is necessary for defense in depth.
**Prevention:** Use `startswith(".env")` for environment files (with an exception for `.env.example`) and maintain an extensive list of sensitive extensions (`.pem`, `.key`, `.gpg`, etc.) and credential filenames.
