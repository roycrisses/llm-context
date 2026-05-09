## 2025-05-15 - Immediate Token Feedback
**Learning:** For LLM-related CLI tools, providing a summary of token counts and file counts via stderr is highly valuable. It allows users to monitor their context budget without breaking the ability to pipe the main stdout to other tools or files.
**Action:** Always include a non-intrusive summary in stderr when generating context blocks.

## 2025-05-15 - Sensible CLI Defaults
**Learning:** Requiring a directory argument (even if it's just '.') adds unnecessary friction for the common case of scanning the current project.
**Action:** Default directory arguments to '.' where appropriate.

## 2025-05-16 - Granular Context Feedback
**Learning:** Users need to know not just THAT files were included, but HOW they were included. Distinguishing between full, truncated, and omitted files helps users debug why their LLM might be missing information and manages expectations about the context quality.
**Action:** Provide granular counts for truncated and omitted files in context summaries.
