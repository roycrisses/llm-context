## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-23 - Hardened Scanner against DoS and Sensitive Data Leakage
**Vulnerability:** The scanner would attempt to read non-regular files like FIFOs, which causes it to hang indefinitely (Denial of Service). It also lacked comprehensive exclusions for sensitive files like SSH keys, certificates, and various .env variations.
**Learning:** Checking only for symbolic links is insufficient; one must ensure files are "regular" before attempting to read them to avoid blocking I/O on FIFOs or sockets. Exclusion lists should be proactive in protecting common sensitive file patterns.
**Prevention:** Use `Path.is_file()` to ensure only regular files are processed. Implement broad exclusion rules for `.env*` files (except `.env.example`) and common sensitive extensions/filenames.
