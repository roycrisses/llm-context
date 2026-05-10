## 2025-05-15 - Immediate Token Feedback
**Learning:** For LLM-related CLI tools, providing a summary of token counts and file counts via stderr is highly valuable. It allows users to monitor their context budget without breaking the ability to pipe the main stdout to other tools or files.
**Action:** Always include a non-intrusive summary in stderr when generating context blocks.

## 2025-05-15 - Sensible CLI Defaults
**Learning:** Requiring a directory argument (even if it's just '.') adds unnecessary friction for the common case of scanning the current project.
**Action:** Default directory arguments to '.' where appropriate.

## 2025-05-15 - Visual Cues and Detailed Stats
**Learning:** Adding context-aware emojis to CLI messages provides delightful visual cues that help users quickly identify the status of their request. Furthermore, being explicit about truncated and omitted files improves transparency and trust in the context generation process.
**Action:** Use emojis for status messages and provide granular details on how the context budget was managed.
