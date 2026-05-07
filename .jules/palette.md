## 2025-05-15 - Immediate Token Feedback
**Learning:** For LLM-related CLI tools, providing a summary of token counts and file counts via stderr is highly valuable. It allows users to monitor their context budget without breaking the ability to pipe the main stdout to other tools or files.
**Action:** Always include a non-intrusive summary in stderr when generating context blocks.

## 2025-05-15 - Sensible CLI Defaults
**Learning:** Requiring a directory argument (even if it's just '.') adds unnecessary friction for the common case of scanning the current project.
**Action:** Default directory arguments to '.' where appropriate.

## 2025-05-15 - Visual Polish and Progress Feedback
**Learning:** Adding subtle visual cues like emojis (🚀 for network, 📋 for clipboard) and detailed progress summaries (counts for truncated/omitted files) significantly improves the perceived quality and transparency of CLI tools. It helps users understand why certain files might be missing or shortened without requiring a --verbose flag.
**Action:** Use emojis to signify specific actions and provide granular summaries of background operations.
