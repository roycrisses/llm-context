## 2026-04-18 - Fix path traversal via symbolic links
**Vulnerability:** Path traversal via symbolic links allowed reading files outside the target directory.
**Learning:** `os.walk` includes file symlinks in `filenames`, and `pathlib.Path.read_text()` follows them, potentially leaking sensitive data from outside the intended scan root.
**Prevention:** Always check `is_symlink()` when traversing directories to ensure only local files are processed and avoid following links to sensitive locations.
