## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2025-05-15 - Broaden Sensitive File Exclusions in Scanner
**Vulnerability:** The scanner was including many types of sensitive files by default, such as SSH keys (id_rsa), SSL certificates (.pem, .crt), and varied environment files (.env.secret).
**Learning:** Hardcoded lists of sensitive files (like .env, .env.local) are brittle. A prefix-based approach for .env files is more robust. Common security-sensitive extensions (keys, certs, dumps) should be excluded by default in tools that send code to external APIs.
**Prevention:** Use broad prefix matching for .env files (with an exception for .env.example). Maintain an extensive list of common secret-bearing filenames (SSH keys, .npmrc, .netrc) and extensions (.pem, .key, .sql, .bak).
