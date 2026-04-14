## 2025-05-15 - [Exposed Sensitive Data in Scan Results]
**Vulnerability:** Private keys (e.g., `id_rsa`), certificates (`.pem`, `.key`), and shell history files were not excluded by default, potentially leaking them to LLM providers.
**Learning:** LLM context tools that perform recursive directory scanning must have a robust, "deny-by-default" approach for common sensitive file patterns beyond just `.env` files.
**Prevention:** Maintained a comprehensive list of sensitive extensions and filenames in the core scanner's default exclusion set.
