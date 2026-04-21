# Palette's UX Journal

This journal tracks critical UX and accessibility learnings for the `llm-context` project.

## 2026-04-21 - Defaulting CLI arguments for "Current Directory" tools
**Learning:** For CLI tools that primarily operate on a codebase or directory (like `llm-context`), requiring the user to type `.` every time is a friction point.
**Action:** Default the directory argument to `.` and make it optional. This follows the pattern of tools like `ls`, `git`, and `ruff`. Combined with helpful feedback (like token counts on success), it makes the "happy path" much smoother.
