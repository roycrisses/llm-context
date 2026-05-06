## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.
## 2026-05-06 - Generic Sensitive File Exclusion
**Vulnerability:** Specific sensitive files (like .env.staging and SSH keys) were leaked because the scanner relied on an incomplete hardcoded list of filenames.
**Learning:** Security by enumeration is brittle. A hybrid approach of specific filenames, sensitive extensions, and prefix matching (for .env files) provides much better defense-in-depth.
**Prevention:** Use generic patterns for sensitive file categories (e.g., filename.startswith(".env")) and maintain a comprehensive list of security-related extensions.
