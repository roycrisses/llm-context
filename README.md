# llm-context

[![PyPI version](https://img.shields.io/pypi/v/llm-context.svg)](https://pypi.org/project/llm-context/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Analyze any codebase, find the most relevant files to your question, trim to fit any LLM's token limit, and output a ready-to-use context block — from your terminal.

---

## Install

```bash
pip install llm-context
```

---

## Quick Start

### 1. Diagnose a bug without sending to an LLM (output to terminal)

```bash
llm-context --ask "why is auth broken?"
```

### 2. Send directly to GPT-4 and get an answer

```bash
export OPENAI_API_KEY="sk-..."
llm-context ./src --ask "explain the data models" --model gpt-4 --send
```

### 3. Copy context for Claude and paste it yourself

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
llm-context --ask "refactor to async" --model claude --copy
```

### 4. Save context to a file for later

```bash
llm-context --ask "how does caching work?" --output context.txt
```

### 5. Use with Gemini and override token limit

```bash
export GEMINI_API_KEY="AIza..."
llm-context --ask "summarise this repo" \
  --model gemini --max-tokens 500000 --send
```

### 6. Include/exclude specific file patterns

```bash
llm-context --ask "review API routes" \
  --include "routes/*.py" --exclude "*.test.py" --send
```

---

## All Flags

| Flag | Default | Description |
|---|---|---|
| `--ask / -q` | *(required)* | Your question about the codebase |
| `--model / -m` | `gpt-4o` | Target LLM (controls token budget) |
| `--send` | off | Send to LLM and print response |
| `--copy` | off | Copy context to clipboard |
| `--max-tokens` | model default | Override the token limit |
| `--include` | — | Glob to force-include files (repeatable) |
| `--exclude` | — | Glob to force-exclude files (repeatable) |
| `--output / -o` | — | Save context to a `.txt` file |
| `--verbose / -v` | off | Print progress information to stderr |

---

## Supported Models

| Alias | Provider | Default Token Budget |
|---|---|---|
| `gpt-4o` | OpenAI | 120,000 |
| `gpt-4` | OpenAI | 8,000 |
| `claude` | Anthropic | 180,000 |
| `gemini` | Google | 900,000 |
| `ollama` | Local (Ollama) | 4,000 |

Set the appropriate environment variable before using `--send`:

| Provider | Environment Variable |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Google Gemini | `GEMINI_API_KEY` |
| Ollama | *(none needed — runs locally)* |

---

## How It Works

- **Scans** your project directory recursively, auto-skipping noise like `node_modules/`, `.env`, `__pycache__`, lock files, and binary assets — plus anything in your `.gitignore`.
- **Ranks** every file by relevance to your question using TF-IDF keyword matching, boosted by filename hits and recently-modified files.
- **Trims** the ranked list to fit within the target model's token budget, truncating oversized files intelligently (keeping the top of the file, which is usually the most informative part).

---

## As a Python Library

```python
from llm_context import scan_directory, rank_files, trim_to_budget, build_context_block

files   = scan_directory("./my-project")
ranked  = rank_files(files, query="why is auth broken?")
trimmed = trim_to_budget(ranked, model="gpt-4o")
context = build_context_block(trimmed, query="why is auth broken?", model="gpt-4o")

print(context)
```

Send programmatically:

```python
from llm_context.llm import send

response = send(context, model="gpt-4o")
print(response)
```

---

## Project Structure

```
llm-context/
├── llm_context/
│   ├── __init__.py    # Public API
│   ├── scanner.py     # Directory walker + .gitignore support
│   ├── ranker.py      # TF-IDF relevance scoring
│   ├── trimmer.py     # Token counting + smart trimming
│   ├── context.py     # Context block assembler
│   ├── llm.py         # Multi-provider LLM dispatcher
│   └── cli.py         # Click CLI entrypoint
└── tests/
    ├── test_scanner.py
    ├── test_ranker.py
    └── test_trimmer.py
```

---

## Contributing

Contributions are welcome!

```bash
git clone https://github.com/llm-context/llm-context.git
cd llm-context
pip install -e ".[dev]"

# Run tests
pytest --cov=llm_context tests/

# Lint
ruff check llm_context/
```

Please open an issue before submitting large pull requests.

---

## License

[MIT](https://opensource.org/licenses/MIT) © llm-context contributors
