"""
tests/test_ranker.py — Unit tests for llm_context.ranker
"""

from __future__ import annotations

import time

import pytest

from llm_context.ranker import (
    _filename_boost,
    _recency_boost,
    _term_frequency,
    _tokenize,
    rank_files,
)
from llm_context.scanner import FileInfo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_file(
    rel_path: str,
    content: str = "",
    mtime: float | None = None,
) -> FileInfo:
    """Create a minimal FileInfo for testing."""
    ext = rel_path.rsplit(".", 1)[-1] if "." in rel_path else ""
    return FileInfo(
        path=f"/fake/{rel_path}",
        rel_path=rel_path,
        content=content,
        size=len(content),
        extension=ext,
        mtime=mtime if mtime is not None else time.time() - 86400,  # 1 day ago
    )


# ---------------------------------------------------------------------------
# _tokenize
# ---------------------------------------------------------------------------


class TestTokenize:
    def test_basic_words(self):
        tokens = _tokenize("hello world")
        assert "hello" in tokens
        assert "world" in tokens

    def test_camelcase_split(self):
        tokens = _tokenize("getUserName")
        # Should contain both full and split forms
        assert "getusername" in tokens or "username" in tokens

    def test_numbers_ignored(self):
        # Purely numeric tokens are not captured by _TOKEN_RE
        tokens = _tokenize("value = 42")
        assert "42" not in tokens

    def test_empty_string(self):
        assert _tokenize("") == []

    def test_lowercase(self):
        tokens = _tokenize("Auth LOGIN")
        assert "auth" in tokens
        assert "login" in tokens


# ---------------------------------------------------------------------------
# _term_frequency
# ---------------------------------------------------------------------------


class TestTermFrequency:
    def test_counts_correctly(self):
        tf = _term_frequency(["a", "b", "a", "c", "a"])
        assert tf["a"] == 3
        assert tf["b"] == 1

    def test_empty(self):
        assert _term_frequency([]) == {}


# ---------------------------------------------------------------------------
# _filename_boost
# ---------------------------------------------------------------------------


class TestFilenameBoost:
    def test_boost_when_match(self):
        boost = _filename_boost("src/auth.py", ["auth", "login"])
        assert boost > 0.0

    def test_no_boost_when_no_match(self):
        boost = _filename_boost("src/utils.py", ["database", "query"])
        assert boost == 0.0

    def test_boost_scales_with_hits(self):
        single = _filename_boost("auth_login.py", ["auth"])
        double = _filename_boost("auth_login.py", ["auth", "login"])
        assert double > single


# ---------------------------------------------------------------------------
# _recency_boost
# ---------------------------------------------------------------------------


class TestRecencyBoost:
    def test_very_recent_file_gets_boost(self):
        now = time.time()
        assert _recency_boost(now) > 0.0

    def test_old_file_gets_no_boost(self):
        old = time.time() - (30 * 24 * 3600)  # 30 days ago
        assert _recency_boost(old) == 0.0

    def test_future_mtime_gets_max_boost(self):
        future = time.time() + 3600
        assert _recency_boost(future) == pytest.approx(0.10)

    def test_week_old_file_gets_some_boost(self):
        week_ago = time.time() - (6 * 24 * 3600)
        boost = _recency_boost(week_ago)
        assert 0.0 < boost < 0.10


# ---------------------------------------------------------------------------
# rank_files
# ---------------------------------------------------------------------------


class TestRankFiles:
    def test_raises_on_empty_query(self):
        files = [make_file("a.py", "x = 1")]
        with pytest.raises(ValueError, match="non-empty"):
            rank_files(files, "")

    def test_raises_on_whitespace_query(self):
        files = [make_file("a.py")]
        with pytest.raises(ValueError):
            rank_files(files, "   ")

    def test_returns_empty_for_no_files(self):
        assert rank_files([], "auth") == []

    def test_relevant_file_ranked_first(self):
        auth_file = make_file("auth.py", "def login(user, password): ...")
        utils_file = make_file("utils.py", "def format_date(d): ...")
        model_file = make_file("model.py", "class User: email: str")

        ranked = rank_files([utils_file, model_file, auth_file], "fix auth login bug")
        assert ranked[0]["rel_path"] == "auth.py"

    def test_preserves_all_files(self):
        files = [make_file(f"f{i}.py", f"content {i}") for i in range(5)]
        ranked = rank_files(files, "content")
        assert len(ranked) == len(files)

    def test_filename_match_boosts_rank(self):
        database_file = make_file("database.py", "import sqlite3")
        config_file = make_file("config.py", "DATABASE_URL = 'sqlite:///db.sqlite3'")

        # "database" matches filename of database.py exactly
        ranked = rank_files([config_file, database_file], "database connection")
        assert ranked[0]["rel_path"] == "database.py"

    def test_recently_modified_file_boosted(self):
        old_file = make_file("old.py", "auth login password", mtime=time.time() - 1_000_000)
        recent_file = make_file("recent.py", "auth login password", mtime=time.time() - 60)

        ranked = rank_files([old_file, recent_file], "auth")
        # Same content, but recent file should rank higher or equal
        assert ranked[0]["rel_path"] == "recent.py"

    def test_single_file_returns_single(self):
        f = make_file("only.py", "x = 1")
        ranked = rank_files([f], "variables")
        assert len(ranked) == 1
        assert ranked[0]["rel_path"] == "only.py"

    def test_ranking_is_deterministic(self):
        files = [make_file(f"file{i}.py", f"def func_{i}(): pass") for i in range(10)]
        r1 = rank_files(files, "function")
        r2 = rank_files(files, "function")
        assert [f["rel_path"] for f in r1] == [f["rel_path"] for f in r2]

    def test_camelcase_split_fixed(self):
        tokens = _tokenize("getUserName")
        assert "get" in tokens
        assert "user" in tokens
        assert "name" in tokens
        assert "getusername" in tokens

    def test_snake_case_split(self):
        tokens = _tokenize("get_user_name")
        assert "get" in tokens
        assert "user" in tokens
        assert "name" in tokens
        assert "get_user_name" in tokens
