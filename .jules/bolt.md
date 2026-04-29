# Bolt's Performance Journal

This journal contains critical learnings and insights discovered while optimizing the `llm-context` codebase.

## Mission
Identify and implement performance improvements that make the application measurably faster or more efficient, focusing on clean, under 50-line changes.

## 2025-05-15 - Initial Performance Baseline
**Learning:** Established baseline for ranking performance: ~0.16s for 1000 files. Tokenization currently has a bug that doubles tokens for camelCase/snake_case and fails to split them correctly due to premature lowercasing.
**Action:** Optimize TF-IDF calculation and fix tokenization logic to improve both speed and accuracy.
