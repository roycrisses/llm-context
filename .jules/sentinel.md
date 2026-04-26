## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-26 - Prevent DoS via FIFOs and Data Leakage of Credentials
**Vulnerability:** The scanner was not checking if a path was a regular file, leading to potential hangs (DoS) when encountering named pipes (FIFOs) or other special files. It also lacked comprehensive exclusions for common credential files like private SSH keys and `.npmrc`.
**Learning:** Checking `is_file()` is essential because it returns `False` for FIFOs, sockets, and devices, preventing the scanner from blocking on them. Automated codebase analysis tools must be extremely aggressive in excluding identity and credential files.
**Prevention:** Always use `is_file()` to ensure you are only reading regular files. Maintain an extensive deny-list of sensitive extensions (PEM, KEY, CRT) and filenames (id_rsa, .npmrc) to prevent accidental inclusion of secrets in LLM context.
