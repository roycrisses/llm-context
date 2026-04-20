## 2025-05-15 - Informative CLI Success Messages
**Learning:** In CLI tools that generate large amounts of data (like LLM context blocks), simple success messages like "Copied to clipboard" can leave users uncertain about the actual scope of what was processed. Providing quantifiable feedback (e.g., file count and total token count) immediately validates the outcome and helps users ensure they are within their model's budget before pasting.
**Action:** Always include key metrics (counts, sizes, or durations) in success notifications for data-processing CLI tasks.
