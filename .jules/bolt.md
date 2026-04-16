## 2025-05-15 - [TF-IDF Scoring & Tokenization Optimization]
**Learning:** Performing `text.lower()` before camelCase splitting logic prevents detection of word boundaries. Algorithmic complexity in ranking can be significantly reduced by calculating term frequencies only for query keywords and using sets for document frequency checks.
**Action:** Always process tokens before lowercasing when word boundary detection (camelCase) is required. Use set-based lookups and pre-calculated values (like IDF) to optimize O(Q*N*L) operations in ranking algorithms.
