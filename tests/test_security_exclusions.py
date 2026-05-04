"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from pathlib import Path
import pytest
from llm_context.scanner import scan_directory

def test_security_exclusions(tmp_path: Path):
    """Verify that various sensitive files are excluded from scans."""
    # Create sensitive files
    (tmp_path / ".env.staging").write_text("SECRET=leaked", encoding="utf-8")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY", encoding="utf-8")
    (tmp_path / "private.pem").write_text("PEM KEY", encoding="utf-8")
    (tmp_path / ".npmrc").write_text("token=abc", encoding="utf-8")
    (tmp_path / "config.key").write_text("SECRET KEY", encoding="utf-8")
    (tmp_path / ".env.example").write_text("TEMPLATE=val", encoding="utf-8")
    (tmp_path / "normal.txt").write_text("safe", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # These should be excluded
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert "config.key" not in rel_paths

    # These should be included
    assert "normal.txt" in rel_paths
    assert ".env.example" in rel_paths

def test_dot_env_variations(tmp_path: Path):
    """Verify various .env.* patterns are caught."""
    (tmp_path / ".env.test").write_text("...", encoding="utf-8")
    (tmp_path / ".env.local.db").write_text("...", encoding="utf-8")
    (tmp_path / ".envrc").write_text("...", encoding="utf-8") # direnv
    (tmp_path / "normal.py").write_text("print(1)", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert ".env.test" not in rel_paths
    assert ".env.local.db" not in rel_paths
    assert ".envrc" not in rel_paths
    assert "normal.py" in rel_paths
