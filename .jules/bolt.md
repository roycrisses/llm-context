## 2025-05-15 - Optimizing Ranker Performance

**Learning:** The `_tokenize` function was a major bottleneck due to redundant regex operations. Specifically, calling `re.sub` for camelCase splitting on every single token, regardless of whether it could actually be a camelCase word (e.g., all lowercase words), caused significant overhead. Additionally, the TF-IDF calculation was inefficient for large document sets because it recalculated IDF values repeatedly and used linear searches for document frequency.

**Action:**
1. Add a fast-path in `_tokenize` to skip `re.sub` for tokens that don't contain uppercase letters or underscores.
2. Optimize `_compute_tfidf_scores` by pre-calculating IDF values and using sets for fast document frequency lookups.
3. Postpone `.lower()` in `_tokenize` to allow for correct camelCase detection.
