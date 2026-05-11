## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-11 - Comprehensive Exclusion of Sensitive Files and Environment Variants
**Vulnerability:** The scanner was only excluding a handful of specific `.env` files and was missing common sensitive files like SSH private keys (`id_rsa`), credential files (`.npmrc`, `.netrc`), and various certificate/key extensions (`.pem`, `.key`, `.crt`).
**Learning:** Attackers often look for specific filenames and extensions to find secrets. A blacklist should cover common patterns and variants of sensitive files.
**Prevention:** Implement a broad exclusion strategy that includes all `.env.*` variants (except examples), common SSH key filenames, and security-related file extensions. Use regression tests to ensure these files are never accidentally included.
