## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2024-05-20 - Enhanced Sensitive File Exclusions
**Vulnerability:** The scanner was not excluding common sensitive files like `.env.staging`, SSH private keys (`id_rsa`), and credential files (`.npmrc`, `.netrc`).
**Learning:** A fixed list of environment files is insufficient; a prefix-based match (e.g., `.env*`) is safer while allowing specific exceptions like `.env.example`.
**Prevention:** Use a combination of robust extension-based (`.pem`, `.key`) and filename-based exclusions for known secret patterns. Always allow `.env.example` as it is intended for context.
