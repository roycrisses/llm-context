## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-15 - Hardening Scanner Against Sensitive and Non-Regular Files
**Vulnerability:** The scanner could include sensitive configuration files (.npmrc, .netrc), SSH private keys, and non-regular files like UNIX sockets or FIFOs. It also didn't consistently block all .env variants (e.g., .env.test).
**Learning:** For a tool that exports codebase context, a "deny-list" approach for sensitive files must be comprehensive. Furthermore, reading from non-regular files can cause the scanner to hang or crash if it encounters a named pipe or socket.
**Prevention:** Use `pathlib.Path.is_file()` to ensure only regular files are processed. Implement a strict prefix match for `.env*` files with an explicit allow-list for safe files like `.env.example`.
