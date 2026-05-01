## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-20 - Expanded Sensitive File Filtering for LLM Context
**Vulnerability:** Common naming conventions for sensitive files (like `.env.staging`, SSH keys, or `.npmrc`) were not fully covered by the scanner's exclusion list, potentially leaking secrets to LLMs.
**Learning:** Fixed lists of `.env` files are insufficient. A more robust approach is to exclude all files starting with `.env` (except `.env.example`) and to maintain a broad list of "secret-prone" extensions like `.pem`, `.key`, and `.gpg`.
**Prevention:** Use prefix-based matching for environment files and proactively block a wide range of cryptographic and configuration file types that typically contain credentials.
