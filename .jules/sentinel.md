## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-03 - Comprehensive Exclusion of Sensitive Files and Prevention of DoS via FIFOs
**Vulnerability:** The scanner was vulnerable to a Denial of Service (DoS) if it encountered a named pipe (FIFO) or device file, as it would block indefinitely on reading. It also failed to exclude several common sensitive file patterns like `.npmrc`, SSH private keys, and varied `.env` suffixes.
**Learning:** Checking for `is_file()` is critical when recursively scanning directories to avoid blocking on special files. Sensitive file lists need to be proactive and cover common credential-bearing formats and naming conventions.
**Prevention:** Always use `is_file()` to ensure only regular files are processed. Use prefix matching for `.env*` files (allowing `.env.example`) and maintain an exhaustive list of known sensitive filenames and extensions.
