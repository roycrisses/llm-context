## 2025-05-15 - Symlink Path Traversal in Scanner
**Vulnerability:** The `scanner.py` module followed symbolic links, allowing it to read and expose files outside the intended project root.
**Learning:** By default, `os.walk` does not follow symlinks for directories unless `followlinks=True` is set, but it does return symlinks to files in the `filenames` list. Accessing these symlinks can lead to sensitive data leakage if they point outside the scanned directory.
**Prevention:** Explicitly check if a file is a symbolic link using `pathlib.Path.is_symlink()` and skip it during directory traversal if symbolic links are not intended to be supported.
