## 2025-05-15 - Immediate Token Feedback
**Learning:** For LLM-related CLI tools, providing a summary of token counts and file counts via stderr is highly valuable. It allows users to monitor their context budget without breaking the ability to pipe the main stdout to other tools or files.
**Action:** Always include a non-intrusive summary in stderr when generating context blocks.

## 2025-05-15 - Sensible CLI Defaults
**Learning:** Requiring a directory argument (even if it's just '.') adds unnecessary friction for the common case of scanning the current project.
**Action:** Default directory arguments to '.' where appropriate.

## 2025-05-15 - Progress Visibility for Slow Operations
**Learning:** When a CLI tool performs a network request that can take several seconds (like sending context to an LLM), providing an immediate "Sending..." indicator with a visual cue (like 🚀) is essential to prevent the user from thinking the tool has hung.
**Action:** Always provide an immediate status indicator before starting long-running network or I/O operations.
