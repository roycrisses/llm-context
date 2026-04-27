# Palette's Journal - llm-context

## 2025-05-14 - Default CLI directory to current path
**Learning:** Users often run CLI tools from the root of the project they are analyzing. Requiring an explicit `.` argument is a small but frequent friction point.
**Action:** Make the `DIRECTORY` argument optional in the CLI, defaulting to the current directory (`.`).
