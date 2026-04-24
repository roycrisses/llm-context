## 2025-05-14 - Ranker Optimization
**Learning:** TF-IDF ranking with many files was slow (~2.3s for 1000 files) due to O(N*L) list lookups for Document Frequency, repeated IDF calculations, and redundant tokenization logic in `_tokenize`.
**Action:** Use sets for DF lookups, pre-calculate IDFs, filter TF by query terms, and optimize `_tokenize` to skip regex for simple tokens and fix camelCase splitting.
