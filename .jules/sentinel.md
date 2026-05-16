## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.
## 2026-05-16 - Fix Sensitive File Leakage in Scanner
**Vulnerability:** The scanner was including sensitive files like SSH keys (id_rsa, etc.), .npmrc, and various .env variants (e.g., .env.staging), potentially exposing secrets to LLMs.
**Learning:** A "secure by default" approach is critical for context-gathering tools. Relying only on a basic list of .env files is insufficient when users often use environment-specific suffixes.
**Prevention:** Use prefix-based matching for sensitive files like .env and maintain a comprehensive, categorized list of excluded extensions (e.g., certificates, keys) and filenames (e.g., SSH keys, auth configs).
