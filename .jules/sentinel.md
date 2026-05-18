## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-04-21 - Robust Security Exclusions for Sensitive Files
**Vulnerability:** The scanner only excluded exactly ".env", allowing variants like ".env.staging" or ".env.local" to be leaked. It also lacked exclusions for SSH private keys, certificates, and database dumps.
**Learning:** Security blacklists must account for common naming conventions and extensions used for secrets. Relying on exact filename matches for ".env" is insufficient.
**Prevention:** Use prefix-based matching for sensitive configuration files (e.g., starts with ".env") while allowing safe templates (e.g., ".env.example"). Maintain a comprehensive list of sensitive extensions (.pem, .key, .sql, etc.) and filenames (id_rsa, .npmrc).
