## 2025-05-23 - Symlink Path Traversal in Directory Scanner
**Vulnerability:** The directory scanner followed symbolic links, allowing it to read and include files from outside the target root directory in the LLM context block.
**Learning:** Tools that recursively walk user-provided directories must explicitly handle or skip symbolic links to prevent "jailbreaking" the intended scope and leaking sensitive system files.
**Prevention:** Use `path.is_symlink()` to detect and skip symbolic links during directory traversal and file processing. In Python's `os.walk`, also prune directory symlinks from the `dirnames` list in-place.
