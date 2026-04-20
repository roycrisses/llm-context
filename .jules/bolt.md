## 2025-05-15 - TF-IDF and Tokenization Optimization
**Learning:** In a codebase analyzer, the ranking engine is a primary bottleneck. Tokenization with repeated `re.sub` and pre-lowercasing text is expensive and can break semantic splitting (camelCase). TF-IDF calculations benefit significantly from $O(1)$ set lookups for Document Frequency and pre-calculating IDF values outside the document loop.
**Action:** Always preserve case until token splitting is done, skip expensive regex when simple strings suffice, and use sets for membership tests in large collections.
