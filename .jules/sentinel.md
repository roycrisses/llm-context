## 2026-04-20 - Prevent Path Traversal and Sensitive Data Leakage in Scanner
**Vulnerability:** The scanner was following symbolic links, which could allow access to sensitive files outside the scanned directory or cause infinite recursion. It also included shell history files which often contain secrets.
**Learning:** For a codebase context tool, following symlinks by default is a security risk. Standard libraries like `os.walk` follow directory symlinks if they are not pruned from `dirnames`.
**Prevention:** Always explicitly check for and skip symbolic links when walking directories unless specifically required. Maintain a robust list of excluded filenames for sensitive artifacts like history files.

## 2026-05-02 - Enhanced Sensitive File Exclusions and Scanner Robustness
**Vulnerability:** The scanner was potentially including sensitive files like `.npmrc`, SSH private keys, and various `.env` variants (e.g., `.env.staging`), which could lead to accidental exposure of secrets when building LLM context. It was also not explicitly skipping non-regular files (like FIFOs), which could cause the scanner to hang or crash (DoS).
**Learning:** Default exclusion lists should be broad and proactive. Hardcoding specific `.env` files is insufficient; a prefix-based match is more robust.
**Prevention:** Use prefix matching for sensitive files like `.env*`. Maintain an extensive list of sensitive extensions (PEM, CRT, KEY, etc.) and filenames. Always verify that files are regular files before attempting to read them.
