## 2025-05-15 - [Intelligent Tokenization for Search UX]
**Learning:** Tokenization for codebase search must process tokens *before* lowercasing to preserve camelCase and snake_case patterns. If lowercased too early, sub-token extraction (e.g., AuthService -> auth, service) fails, leading to poor relevance and a frustrating user experience.
**Action:** Always ensure regex-based splitting of composite identifiers occurs on the original case-sensitive string.

## 2025-05-15 - [Graceful Budget Exhaustion]
**Learning:** Small token budgets (e.g., --max-tokens 200) are easily exhausted by fixed overhead (headers/footers), leading to empty results. This feels like a bug to the user.
**Action:** Implement dynamic overhead reservation: skip fixed overhead if the total budget is smaller than the default overhead limit, allowing at least some content to be included.
