## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2024-05-15 - Expanded Sensitive Data Exclusions and Special File Handling
**Vulnerability:** The scanner was not excluding common private keys, certificates, and credential files (e.g., `id_rsa`, `.npmrc`, `.pem`). It also attempted to read from non-regular files like FIFOs, which could cause the tool to hang.
**Learning:** Hardcoded exclusion lists need to be comprehensive to cover the wide variety of sensitive artifacts produced by modern dev tools. Additionally, `pathlib.Path.is_file()` is essential to distinguish between regular text files and special files that shouldn't be read.
**Prevention:** Maintain an extensive blocklist of sensitive extensions and filenames. Always verify that a path refers to a regular file before attempting to read its content.
