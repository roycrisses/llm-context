## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-12 - Critical Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was gathering sensitive files like SSH private keys (`id_rsa`), configuration files with auth tokens (`.npmrc`), and all `.env` variants (e.g., `.env.staging`, `.env.secret`) as context for LLMs.
**Learning:** Default file scanning in developer tools must be "secure by default" specifically regarding secrets. Relying on `.gitignore` is insufficient as developers often don't ignore files they intend to keep locally but shouldn't share with an LLM.
**Prevention:** Implement a hardcoded, robust blocklist of sensitive filenames and extensions. Use prefix-based matching for `.env` files while explicitly allowing harmless examples like `.env.example`.
