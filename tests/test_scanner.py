"""
tests/test_scanner.py — Unit tests for llm_context.scanner
"""

from __future__ import annotations

from pathlib import Path

import pytest

from llm_context.scanner import (
    _load_gitignore_patterns,
    _matches_gitignore,
    _should_skip_dir,
    _should_skip_file,
    scan_directory,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    """Create a minimal fake project tree for testing."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "src" / "auth.py").write_text("def login(): pass", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Project", encoding="utf-8")
    (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "lodash.js").write_text("//lib", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "main.cpython-311.pyc").write_bytes(b"\x00\x01\x02")
    (tmp_path / "logo.png").write_bytes(b"\x89PNG")
    (tmp_path / ".env").write_text("SECRET=abc", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# _should_skip_dir
# ---------------------------------------------------------------------------


class TestShouldSkipDir:
    def test_excludes_node_modules(self):
        assert _should_skip_dir("node_modules") is True

    def test_excludes_pycache(self):
        assert _should_skip_dir("__pycache__") is True

    def test_excludes_dot_directories(self):
        assert _should_skip_dir(".git") is True
        assert _should_skip_dir(".venv") is True

    def test_allows_src(self):
        assert _should_skip_dir("src") is False

    def test_allows_lib(self):
        assert _should_skip_dir("lib") is False


# ---------------------------------------------------------------------------
# _should_skip_file
# ---------------------------------------------------------------------------


class TestShouldSkipFile:
    def test_excludes_env_file(self):
        assert _should_skip_file(".env", "", ".env", [], None) is True

    def test_excludes_png(self):
        assert _should_skip_file("logo.png", "png", "logo.png", [], None) is True

    def test_excludes_lock_file(self):
        assert _should_skip_file("package-lock.json", "", "package-lock.json", [], None) is True

    def test_allows_python_file(self):
        assert _should_skip_file("main.py", "py", "src/main.py", [], None) is False

    def test_excludes_by_extra_pattern(self):
        assert _should_skip_file("secrets.txt", "txt", "secrets.txt", [], ["secrets.*"]) is True

    def test_gitignore_pattern_match(self):
        assert _should_skip_file("debug.log", "log", "logs/debug.log", ["*.log"], None) is True


# ---------------------------------------------------------------------------
# _load_gitignore_patterns / _matches_gitignore
# ---------------------------------------------------------------------------


class TestGitignore:
    def test_load_empty_when_missing(self, tmp_path: Path):
        patterns = _load_gitignore_patterns(tmp_path)
        assert patterns == []

    def test_load_valid_patterns(self, tmp_path: Path):
        (tmp_path / ".gitignore").write_text(
            "# comment\n\n*.pyc\ndist/\n!important.pyc\n", encoding="utf-8"
        )
        patterns = _load_gitignore_patterns(tmp_path)
        # Comments, empty lines, and negations are skipped
        assert "*.pyc" in patterns
        assert "dist/" in patterns
        assert "# comment" not in patterns
        assert "!important.pyc" not in patterns

    def test_matches_glob_pattern(self):
        assert _matches_gitignore("build/output.js", ["build/"]) is True

    def test_matches_extension_pattern(self):
        assert _matches_gitignore("coverage/lcov.info", ["*.info"]) is True

    def test_no_false_positive(self):
        assert _matches_gitignore("src/main.py", ["*.log", "dist/"]) is False


# ---------------------------------------------------------------------------
# scan_directory
# ---------------------------------------------------------------------------


class TestScanDirectory:
    def test_raises_on_missing_dir(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            scan_directory(tmp_path / "does_not_exist")

    def test_raises_on_file_path(self, tmp_path: Path):
        f = tmp_path / "file.py"
        f.write_text("x = 1")
        with pytest.raises(NotADirectoryError):
            scan_directory(f)

    def test_finds_python_files(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        rel_paths = [f["rel_path"] for f in files]
        assert any("main.py" in p for p in rel_paths)
        assert any("auth.py" in p for p in rel_paths)

    def test_finds_markdown(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        rel_paths = [f["rel_path"] for f in files]
        assert any("README.md" in p for p in rel_paths)

    def test_excludes_node_modules(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        rel_paths = [f["rel_path"] for f in files]
        assert not any("node_modules" in p for p in rel_paths)

    def test_excludes_pycache(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        rel_paths = [f["rel_path"] for f in files]
        assert not any("__pycache__" in p for p in rel_paths)

    def test_excludes_png(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        rel_paths = [f["rel_path"] for f in files]
        assert not any("logo.png" in p for p in rel_paths)

    def test_excludes_env(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        rel_paths = [f["rel_path"] for f in files]
        assert not any(".env" in p for p in rel_paths)

    def test_excludes_lock_file(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        rel_paths = [f["rel_path"] for f in files]
        assert not any("package-lock.json" in p for p in rel_paths)

    def test_fileinfo_fields_present(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        assert len(files) > 0
        for f in files:
            assert "path" in f
            assert "rel_path" in f
            assert "content" in f
            assert "size" in f
            assert "extension" in f
            assert "mtime" in f

    def test_content_is_string(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        for f in files:
            assert isinstance(f["content"], str)

    def test_extra_include_overrides_exclusion(self, tmp_project: Path):
        # Force-include the .env file
        files = scan_directory(tmp_project, extra_includes=[".env"])
        rel_paths = [f["rel_path"] for f in files]
        assert any(".env" in p for p in rel_paths)

    def test_extra_exclude_removes_file(self, tmp_project: Path):
        files = scan_directory(tmp_project, extra_excludes=["*.md"])
        rel_paths = [f["rel_path"] for f in files]
        assert not any(p.endswith(".md") for p in rel_paths)

    def test_respects_gitignore(self, tmp_project: Path):
        (tmp_project / ".gitignore").write_text("src/auth.py\n", encoding="utf-8")
        files = scan_directory(tmp_project)
        rel_paths = [f["rel_path"] for f in files]
        assert not any("auth.py" in p for p in rel_paths)

    def test_returns_sorted_by_rel_path(self, tmp_project: Path):
        files = scan_directory(tmp_project)
        paths = [f["rel_path"] for f in files]
        assert paths == sorted(paths)

    def test_empty_directory(self, tmp_path: Path):
        files = scan_directory(tmp_path)
        assert files == []

    def test_skips_symlinks(self, tmp_path: Path):
        (tmp_path / "real_file.txt").write_text("content")
        (tmp_path / "link.txt").symlink_to(tmp_path / "real_file.txt")

        # External file link
        external_file = tmp_path.parent / "external.txt"
        external_file.write_text("external content")
        (tmp_path / "ext_link.txt").symlink_to(external_file)

        # Directory link
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir_link").symlink_to(tmp_path / "subdir")

        files = scan_directory(tmp_path)
        rel_paths = [f["rel_path"] for f in files]

        assert "real_file.txt" in rel_paths
        assert "link.txt" not in rel_paths
        assert "ext_link.txt" not in rel_paths
        assert "subdir_link" not in rel_paths

    def test_excludes_history_files(self, tmp_path: Path):
        (tmp_path / ".bash_history").write_text("history")
        (tmp_path / ".zsh_history").write_text("history")
        (tmp_path / "normal.txt").write_text("normal")

        files = scan_directory(tmp_path)
        rel_paths = [f["rel_path"] for f in files]

        assert "normal.txt" in rel_paths
        assert ".bash_history" not in rel_paths
        assert ".zsh_history" not in rel_paths

    def test_excludes_sensitive_files(self, tmp_path: Path):
        (tmp_path / "id_rsa").write_text("private key")
        (tmp_path / "cert.pem").write_text("certificate")
        (tmp_path / ".npmrc").write_text("npm config")
        (tmp_path / "normal.py").write_text("print('hello')")

        files = scan_directory(tmp_path)
        rel_paths = [f["rel_path"] for f in files]

        assert "normal.py" in rel_paths
        assert "id_rsa" not in rel_paths
        assert "cert.pem" not in rel_paths
        assert ".npmrc" not in rel_paths

    def test_refined_env_rules(self, tmp_path: Path):
        (tmp_path / ".env").write_text("SECRET=123")
        (tmp_path / ".env.production").write_text("SECRET=456")
        (tmp_path / ".env.example").write_text("SECRET=your_key")
        (tmp_path / "normal.py").write_text("print('hello')")

        files = scan_directory(tmp_path)
        rel_paths = [f["rel_path"] for f in files]

        assert "normal.py" in rel_paths
        assert ".env.example" in rel_paths
        assert ".env" not in rel_paths
        assert ".env.production" not in rel_paths

    def test_skips_non_regular_files(self, tmp_path: Path):
        import os

        (tmp_path / "normal.txt").write_text("normal content")
        fifo_path = tmp_path / "my_fifo"
        try:
            os.mkfifo(fifo_path)
        except (OSError, AttributeError):
            pytest.skip("FIFOs not supported on this platform")

        files = scan_directory(tmp_path)
        rel_paths = [f["rel_path"] for f in files]

        assert "normal.txt" in rel_paths
        assert "my_fifo" not in rel_paths
