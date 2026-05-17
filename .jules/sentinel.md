## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-15 - Robust Secret and Sensitive Data Exclusion
**Vulnerability:** The scanner was including sensitive files like `.env.staging`, SSH private keys (`id_rsa`), and database dumps (`.sql`), which could lead to accidental exposure of secrets to LLM providers.
**Learning:** A simple filename-based exclusion list is insufficient. Many sensitive files follow patterns (e.g., all `.env*` variants) or use specific extensions for database exports and backups that must be blocked by default.
**Prevention:** Use a combination of explicit filename matches, extension-based filtering, and prefix-based logic (for `.env`) to create a comprehensive security perimeter. Provide a mechanism for users to explicitly override these if necessary, while keeping the default state secure.
