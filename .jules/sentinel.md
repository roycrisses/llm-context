## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-21 - Comprehensive Sensitive File Exclusion in Codebase Scanner
**Vulnerability:** The scanner only excluded exactly `.env`, allowing leaks of variants like `.env.staging` or `.env.local`. It also lacked exclusions for common private key formats (SSH keys, PEM files) and package manager credentials (`.npmrc`).
**Learning:** Default-deny is safer for scanners. Relying on exact filename matches for sensitive files is brittle because developers often use environment-specific suffixes.
**Prevention:** Use prefix-based matching for `.env` files (excluding `.env.example`). Maintain an exhaustive list of sensitive extensions (`.pem`, `.key`, `.crt`) and common credential filenames.
