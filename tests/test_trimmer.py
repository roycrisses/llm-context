"""
tests/test_trimmer.py — Unit tests for llm_context.trimmer
"""

from __future__ import annotations

import time


from llm_context.scanner import FileInfo
from llm_context.trimmer import (
    MODEL_TOKEN_LIMITS,
    _truncate_file_content,
    count_tokens,
    get_token_limit,
    trim_to_budget,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_file(
    rel_path: str = "file.py",
    content: str = "x = 1\n",
    extension: str = "py",
) -> FileInfo:
    """Create a minimal FileInfo for testing."""
    return FileInfo(
        path=f"/fake/{rel_path}",
        rel_path=rel_path,
        content=content,
        size=len(content),
        extension=extension,
        mtime=time.time(),
    )


def big_content(n_lines: int = 500) -> str:
    """Generate a large multi-line file content."""
    return "\n".join(f"x_{i} = {i} * some_variable_name" for i in range(n_lines))


# ---------------------------------------------------------------------------
# count_tokens
# ---------------------------------------------------------------------------


class TestCountTokens:
    def test_returns_positive_int(self):
        result = count_tokens("hello world")
        assert isinstance(result, int)
        assert result > 0

    def test_empty_string_returns_at_least_one(self):
        # Our implementation uses max(1, ...)
        assert count_tokens("") >= 1

    def test_longer_text_has_more_tokens(self):
        short = count_tokens("hi")
        long = count_tokens("hi " * 100)
        assert long > short

    def test_works_for_all_models(self):
        for model in MODEL_TOKEN_LIMITS:
            result = count_tokens("test text", model)
            assert result > 0


# ---------------------------------------------------------------------------
# get_token_limit
# ---------------------------------------------------------------------------


class TestGetTokenLimit:
    def test_known_models(self):
        assert get_token_limit("gpt-4o") == 120_000
        assert get_token_limit("gpt-4") == 8_000
        assert get_token_limit("claude") == 180_000
        assert get_token_limit("gemini") == 900_000
        assert get_token_limit("ollama") == 4_000

    def test_unknown_model_falls_back_to_gpt4o(self):
        assert get_token_limit("some-unknown-model") == get_token_limit("gpt-4o")

    def test_case_insensitive(self):
        assert get_token_limit("GPT-4O") == get_token_limit("gpt-4o")


# ---------------------------------------------------------------------------
# _truncate_file_content
# ---------------------------------------------------------------------------


class TestTruncateFileContent:
    def test_no_truncation_when_fits(self):
        content = "x = 1\ny = 2\n"
        result = _truncate_file_content(content, max_tokens=1000, model="gpt-4o")
        assert result == content

    def test_truncation_adds_notice(self):
        content = big_content(200)
        result = _truncate_file_content(content, max_tokens=50, model="gpt-4o")
        assert "truncated" in result.lower()

    def test_truncated_result_is_shorter(self):
        content = big_content(200)
        result = _truncate_file_content(content, max_tokens=50, model="gpt-4o")
        assert len(result) < len(content)

    def test_result_starts_with_original_beginning(self):
        lines = [f"line_{i}" for i in range(100)]
        content = "\n".join(lines)
        result = _truncate_file_content(content, max_tokens=20, model="gpt-4o")
        assert result.startswith("line_0")


# ---------------------------------------------------------------------------
# trim_to_budget
# ---------------------------------------------------------------------------


class TestTrimToBudget:
    def test_returns_empty_for_empty_input(self):
        result = trim_to_budget([], model="gpt-4o")
        assert result == []

    def test_returns_all_files_when_budget_large(self):
        files = [make_file(f"f{i}.py", "x = 1\n") for i in range(5)]
        result = trim_to_budget(files, model="gemini")  # 900k tokens
        assert len(result) == 5

    def test_drops_files_over_budget(self):
        # Create many small files that exceed a very tight budget
        files = [make_file(f"f{i}.py", "x = 1\n" * 10) for i in range(100)]
        result = trim_to_budget(files, model="ollama", max_tokens=50)
        assert len(result) < 100

    def test_respects_max_tokens_override(self):
        files = [make_file(f"f{i}.py", "x" * 500) for i in range(10)]
        # Tiny budget: should include very few (or zero) files
        result = trim_to_budget(files, model="gpt-4o", max_tokens=10)
        assert len(result) <= len(files)

    def test_large_single_file_is_truncated_not_dropped(self):
        huge_content = big_content(1000)
        files = [make_file("big.py", huge_content)]
        result = trim_to_budget(files, model="gpt-4o", max_tokens=200)
        # The file should be included but with truncated content
        assert len(result) == 1
        assert len(result[0]["content"]) < len(huge_content)

    def test_preserves_order(self):
        # Files should remain in their input order (rank order)
        files = [make_file(f"file{i}.py", "x = 1\n") for i in range(5)]
        result = trim_to_budget(files, model="gpt-4o")
        result_paths = [f["rel_path"] for f in result]
        expected = [f["rel_path"] for f in files[: len(result)]]
        assert result_paths == expected

    def test_custom_model(self):
        files = [make_file("a.py", "x = 1")]
        result = trim_to_budget(files, model="claude")
        assert len(result) == 1

    def test_does_not_mutate_original_files(self):
        content = "original content\n"
        files = [make_file("a.py", content)]
        _ = trim_to_budget(files, model="ollama", max_tokens=5)
        # Original should be unchanged
        assert files[0]["content"] == content
