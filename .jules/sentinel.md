## 2025-05-15 - Symlink Path Traversal in Scanner
**Vulnerability:** The directory scanner followed symbolic links by default, allowing a user to include files outside the scanned directory (e.g., `/etc/passwd`) in the context block sent to an LLM.
**Learning:** Tools that recursively walk user-provided directories must explicitly handle symbolic links to avoid path traversal. `os.walk` doesn't follow symlinks to *directories* by default, but it does include symlinks to *files* in the `filenames` list, and `pathlib.Path.read_text()` or `open()` will follow them.
**Prevention:** Use `filepath.is_symlink()` to detect and skip symbolic links unless they are explicitly desired and validated to be within safe boundaries.
