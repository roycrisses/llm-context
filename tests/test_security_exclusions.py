"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_are_excluded(tmp_path: Path):
    """Verify that common sensitive files are excluded from scans."""
    (tmp_path / ".env.staging").write_text("SECRET=leak", encoding="utf-8")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY", encoding="utf-8")
    (tmp_path / "private.pem").write_text("PEM", encoding="utf-8")
    (tmp_path / ".npmrc").write_text("auth_token=123", encoding="utf-8")
    (tmp_path / "normal.txt").write_text("public", encoding="utf-8")
    (tmp_path / ".env.example").write_text("KEY=placeholder", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.txt" in rel_paths
    assert ".env.example" in rel_paths

    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths

def test_env_prefix_exclusion(tmp_path: Path):
    """Verify all .env* files except .env.example are excluded."""
    (tmp_path / ".env").write_text("x", encoding="utf-8")
    (tmp_path / ".env.local").write_text("x", encoding="utf-8")
    (tmp_path / ".env.prod").write_text("x", encoding="utf-8")
    (tmp_path / ".env.example").write_text("x", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert ".env.example" in rel_paths
    assert ".env" not in rel_paths
    assert ".env.local" not in rel_paths
    assert ".env.prod" not in rel_paths

def test_sensitive_extensions_exclusion(tmp_path: Path):
    """Verify files with sensitive extensions are excluded."""
    extensions = ["pem", "crt", "key", "p12", "pfx", "gpg", "pub", "sig", "asc"]
    for ext in extensions:
        (tmp_path / f"cert.{ext}").write_text("sensitive", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    for ext in extensions:
        assert f"cert.{ext}" not in rel_paths
