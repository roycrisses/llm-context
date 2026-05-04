## 2025-05-15 - Immediate Token Feedback
**Learning:** For LLM-related CLI tools, providing a summary of token counts and file counts via stderr is highly valuable. It allows users to monitor their context budget without breaking the ability to pipe the main stdout to other tools or files.
**Action:** Always include a non-intrusive summary in stderr when generating context blocks.

## 2025-05-15 - Sensible CLI Defaults
**Learning:** Requiring a directory argument (even if it's just '.') adds unnecessary friction for the common case of scanning the current project.
**Action:** Default directory arguments to '.' where appropriate.

## 2025-05-20 - Transparent Context Summaries
**Learning:** Users need to know exactly why their context block looks the way it does. Providing explicit counts for truncated and omitted files transforms a "black box" trimming process into a transparent one, helping users adjust their queries or token budgets.
**Action:** Always include truncation and omission details in the CLI summary when they occur.
