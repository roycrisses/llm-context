## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2024-05-15 - Hardening Scanner against Sensitive Data Leakage
**Vulnerability:** The scanner was failing to exclude variations of environment files (e.g., .env.staging) and common SSH private keys/certificates, potentially leaking secrets to LLMs.
**Learning:** Maintaining a list of specific filenames for secrets is brittle. A prefix-based approach for environment files and a broader list of security-related extensions (pem, crt, key) is more robust.
**Prevention:** Use pattern matching for sensitive file categories and maintain a comprehensive blacklist of common credential filenames and extensions.
