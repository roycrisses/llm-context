## 2025-05-15 - [CLI Defaults]
**Learning:** For a codebase analysis tool, the most common use case is scanning the current working directory. Making the directory argument optional and defaulting to `.` significantly reduces typing friction for the user.
**Action:** Always check if positional arguments can have sensible defaults that align with the user's current context (like the working directory).
