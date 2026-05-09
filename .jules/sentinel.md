## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-09 - Prevent Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was not excluding common sensitive files like SSH keys, certificates, and various .env files (e.g., .env.staging), potentially leaking secrets to third-party LLM providers.
**Learning:** LLM-context tools need a very aggressive default exclusion list for sensitive artifacts to ensure "secure by default" behavior.
**Prevention:** Implement a broad list of excluded filenames and extensions, and use prefix-based matching for environment files to catch all variations while allowing safe examples.
