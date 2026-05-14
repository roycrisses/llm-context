## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-14 - Sensitive File Leakage in Repository Scanning
**Vulnerability:** The scanner was including sensitive files like private SSH keys, SSL certificates, and various `.env` environment files, which could lead to accidental exposure of secrets when sent to an LLM.
**Learning:** Default exclusion lists for scanners must be comprehensive and include broad patterns for common secret-containing files (like all `.env*` variants) rather than just a few common names.
**Prevention:** Implement programmatic prefix/suffix checks for high-risk files (e.g., `startswith(".env")`) and maintain an extensive list of sensitive extensions (`.pem`, `.key`, `.p12`) and filenames (`id_rsa`, `.npmrc`).
