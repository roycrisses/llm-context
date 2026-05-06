## 2025-05-15 - Immediate Token Feedback
**Learning:** For LLM-related CLI tools, providing a summary of token counts and file counts via stderr is highly valuable. It allows users to monitor their context budget without breaking the ability to pipe the main stdout to other tools or files.
**Action:** Always include a non-intrusive summary in stderr when generating context blocks.

## 2025-05-15 - Sensible CLI Defaults
**Learning:** Requiring a directory argument (even if it's just '.') adds unnecessary friction for the common case of scanning the current project.
**Action:** Default directory arguments to '.' where appropriate.

## 2025-05-23 - Truncation and Omission Visibility
**Learning:** In LLM context tools, silently dropping or truncating files to fit a budget can lead to confusing results. Informing the user exactly how many files were truncated or omitted provides critical clarity on the "completeness" of the provided context.
**Action:** Explicitly report truncated and omitted file counts in the summary feedback.
