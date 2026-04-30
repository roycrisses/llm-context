## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2024-05-15 - Broaden Sensitive File Exclusions and Harden .env Handling
**Vulnerability:** The scanner only excluded a small set of hardcoded `.env` filenames, leaving other environment files (like `.env.staging` or `.env.local.customer`) potentially exposed. It also lacked exclusions for common sensitive files like SSH private keys, npm/netrc configs, and various certificate/key extensions.
**Learning:** Hardcoding exact filenames for environment variables is insufficient as naming conventions vary. A prefix-based approach is more secure. Additionally, many developers store sensitive credentials in files like `.npmrc` or `.htpasswd` which must be explicitly blacklisted.
**Prevention:** Use `startswith(".env")` to catch all environment file variants, while allowing `.env.example` as a safe template. Maintain a comprehensive list of sensitive extensions (`.pem`, `.key`, `.p12`, etc.) and filenames (`id_rsa`, `.npmrc`) to provide defense in depth.
