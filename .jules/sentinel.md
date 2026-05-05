## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-05 - Enhance Sensitive File Exclusions in Scanner
**Vulnerability:** The scanner lacked comprehensive exclusions for various sensitive files, such as cryptographic keys (.pem, .key), SSH keys (id_rsa), and specific .env variants (e.g., .env.staging). This could result in secrets being sent to an LLM provider.
**Learning:** Default exclusion lists must be aggressive and cover modern development artifacts. A robust prefix-based check for .env files is more effective than listing individual environment files.
**Prevention:** Regularly update exclusion lists with common secret-bearing file patterns. Use prefix-based checks for classes of sensitive files (like .env*) while allowing specific safe templates (.env.example).
