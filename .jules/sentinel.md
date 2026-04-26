## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-26 - Broadened Sensitive File Exclusions
**Vulnerability:** The scanner was capturing sensitive files like private keys (`id_rsa`), certificates (`.pem`), and environment-specific `.env` files (e.g., `.env.staging`), which could leak credentials to an LLM.
**Learning:** Default exclusion lists for developer tools must be aggressive regarding security artifacts. A simple list of exact filenames is often insufficient (e.g., for `.env.local`).
**Prevention:** Use suffix matching for `.env*` files (while allowing `.env.example`) and maintain a comprehensive list of sensitive extensions (`.key`, `.pem`, etc.) and common secret filenames (`id_rsa`, `.token`).
