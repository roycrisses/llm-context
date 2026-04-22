# Palette's Journal - UX & Accessibility Learnings

## 2025-05-15 - CLI Interaction Feedback and Ergonomics
**Learning:** For a tool that generates varying amounts of data (like LLM context), users benefit greatly from seeing immediate descriptive statistics (file count, token count) to understand the "weight" of their request. Additionally, providing immediate feedback for network-bound operations (like `--send`) even in non-verbose mode prevents the CLI from appearing "stuck".
**Action:** Always include summary statistics for data-heavy operations and ensure that asynchronous or network-bound actions have an immediate "Starting..." or "Progress..." indicator.

## 2025-05-15 - Sensible Defaults for CLI Arguments
**Learning:** Defaulting optional positional arguments (like the directory to scan) to the current directory (`.`) aligns with user intuition and significantly reduces repetitive typing for the most common use case.
**Action:** Favor defaulting directory-based positional arguments to `.` when it's safe and expected by the user.
