## 2025-05-15 - Immediate Token Feedback
**Learning:** For LLM-related CLI tools, providing a summary of token counts and file counts via stderr is highly valuable. It allows users to monitor their context budget without breaking the ability to pipe the main stdout to other tools or files.
**Action:** Always include a non-intrusive summary in stderr when generating context blocks.

## 2025-05-15 - Sensible CLI Defaults
**Learning:** Requiring a directory argument (even if it's just '.') adds unnecessary friction for the common case of scanning the current project.
**Action:** Default directory arguments to '.' where appropriate.

## 2025-05-16 - Transparent Context Composition
**Learning:** Users need to know exactly how their token budget was spent. Simply saying "Included 5 files" is insufficient if some of those files were truncated or others were omitted entirely. Detailed counts (included, truncated, omitted) combined with visual emoji cues provide immediate, high-density feedback.
**Action:** Track and report truncation and omission status in summaries. Use emojis to differentiate between scan, rank, trim, and send phases.
