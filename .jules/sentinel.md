## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-28 - Hardening Sensitive File Exclusions
**Vulnerability:** The scanner only excluded a small, hardcoded set of .env files and lacked comprehensive exclusions for common sensitive files like SSH keys, certificates, and configuration files with secrets (e.g., .npmrc).
**Learning:** For LLM context tools, a "deny-by-default" approach for sensitive patterns is safer than an allow-list or a minimal block-list. Using prefix matching for .env files is more robust than listing individual files.
**Prevention:** Implement broad prefix matching for .env files (except .env.example) and maintain a comprehensive list of sensitive extensions (pem, key, crt, etc.) and filenames (id_rsa, .npmrc, etc.).
