## 2025-05-14 - [TF-IDF Document Frequency Optimization]
**Learning:** The initial implementation of document frequency calculation used a nested loop that performed linear scans on token lists (`term in tokens`), resulting in O(M*N*L) complexity. For large codebases and long queries, this becomes a major bottleneck in the ranking phase.
**Action:** Use set-based intersections or pre-calculate sets for each document to reduce membership lookup time. Set intersection `query_set.intersection(doc_set)` is particularly efficient in Python for this purpose.
