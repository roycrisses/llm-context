## 2025-05-15 - Immediate Token Feedback
**Learning:** For LLM-related CLI tools, providing a summary of token counts and file counts via stderr is highly valuable. It allows users to monitor their context budget without breaking the ability to pipe the main stdout to other tools or files.
**Action:** Always include a non-intrusive summary in stderr when generating context blocks.

## 2025-05-15 - Sensible CLI Defaults
**Learning:** Requiring a directory argument (even if it's just '.') adds unnecessary friction for the common case of scanning the current project.
**Action:** Default directory arguments to '.' where appropriate.

## 2025-05-15 - Visual Feedback for CLI Operations
**Learning:** Adding emojis to CLI status messages significantly improves the "delight" factor and makes the output more scannable. Using specific emojis for specific actions (e.g., 💾 for saving, 📋 for copying, 🚀 for network) provides immediate visual context.
**Action:** Use a consistent set of emojis in CLI status messages to denote different types of operations.
