## 2025-05-14 - Sensible Defaults and Active Feedback in CLI
**Learning:** CLI tools feel much more "magical" and intuitive when they assume sensible defaults (like the current directory) and provide explicit feedback for slow, asynchronous operations (like LLM API calls).
**Action:** Default directory arguments to `.` when appropriate, and always show a "Sending..." or "Processing..." status message for network-bound tasks, even if not in verbose mode.
