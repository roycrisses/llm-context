## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-20 - Harden Scanner against DoS and Information Disclosure
**Vulnerability:** Information disclosure of sensitive credentials (SSH keys, .npmrc, .env files) and potential DoS via non-regular files (FIFOs).
**Learning:** Tools that ingest codebase context must be extremely careful not to include secrets. Hardcoded lists of environment files (like .env, .env.local) are insufficient as developers use many variations. Additionally, walking a filesystem and opening files without checking if they are "regular" files (e.g. FIFOs) can cause the tool to hang indefinitely.
**Prevention:** Use broad prefix-based exclusion for environment files (e.g., exclude all .env* except .env.example). Always verify is_file() (not just exists() or not is_symlink()) before attempting to read content to avoid hanging on special files. Maintain an exhaustive list of sensitive extensions (PEM, GPG, etc.) and credential filenames.
