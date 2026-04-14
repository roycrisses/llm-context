## 2025-05-14 - Prevent Symlink Traversal in Scanner
**Vulnerability:** Path traversal via symbolic links. The scanner followed symlinks, which could allow an attacker to include files from outside the target directory (e.g., `/etc/passwd`) in the LLM context if a symlink was present in the scanned directory.
**Learning:** `os.walk` and `pathlib` by default allow access to symlinked files. When scanning directories for context generation, it is crucial to explicitly check for and skip symbolic links unless they are specifically intended to be followed and are validated to stay within bounds.
**Prevention:** Use `filepath.is_symlink()` to detect and skip symbolic links during directory traversal.
