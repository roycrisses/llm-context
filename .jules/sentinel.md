## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-15 - Harden Scanner against Credential Leakage and DoS
**Vulnerability:** The scanner could include highly sensitive files (SSH keys, certificates, cloud credentials) in LLM context. It was also susceptible to DoS if it attempted to read non-regular files like FIFOs or device files.
**Learning:** A codebase scanner must prioritize credential protection by default. Excluding specific extensions (.pem, .key) and filenames (id_rsa, .npmrc) is essential. Furthermore, `pathlib.Path.is_file()` should be used to ensure only regular files are processed.
**Prevention:** Maintain a comprehensive exclusion list for both filenames and extensions. Use a restrictive `.env` exclusion rule that only allows `.env.example`. Always verify that a path is a regular file before attempting to read its content.
