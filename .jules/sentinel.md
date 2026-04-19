## 2026-04-19 - [Path Traversal via Symlinks and History File Exposure]
**Vulnerability:** The scanner followed symbolic links, potentially allowing access to files outside the targeted directory (path traversal). It also included shell and REPL history files in the generated context.
**Learning:** Default directory walking tools like `os.walk` follow symlinks if not explicitly checked, which can leak sensitive system data if a codebase contains links to external paths.
**Prevention:** Always use `is_symlink()` checks when traversing user-provided directories for context gathering and maintain an explicit blocklist for sensitive system-generated files like history.
