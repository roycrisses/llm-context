## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-21 - Non-regular File DoS and Refined Env Protection
**Vulnerability:** The scanner could be blocked by non-regular files like FIFOs (named pipes) if it attempted to read them, leading to a Denial of Service. Additionally, the previous .env exclusion was too broad or too narrow depending on the naming (e.g., .env.production).
**Learning:** `pathlib.Path.is_file()` returns `False` for FIFOs, which is a reliable way to filter them out along with `is_symlink()`. For environment files, a "deny-all-except-example" policy is safer than an enumeration of known .env suffixes.
**Prevention:** Use `is_file()` to ensure only regular files are processed. Implement a prefix-based exclusion for `.env` files with an explicit allow-list for templates like `.env.example`.
