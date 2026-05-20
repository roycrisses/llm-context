"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_file_exclusions(tmp_path: Path):
    """Verify that sensitive files and extensions are correctly excluded."""
    (tmp_path / "id_rsa").write_text("PRIVATE KEY")
    (tmp_path / "id_ed25519").write_text("PRIVATE KEY")
    (tmp_path / ".npmrc").write_text("token=abc")
    (tmp_path / "cert.pem").write_text("CERTIFICATE")
    (tmp_path / "database.sql").write_text("SELECT * FROM users")
    (tmp_path / "backup.bak").write_text("backup data")
    (tmp_path / "private.key").write_text("key data")
    (tmp_path / "public.txt").write_text("hello world")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "public.txt" in rel_paths
    assert "id_rsa" not in rel_paths
    assert "id_ed25519" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert "cert.pem" not in rel_paths
    assert "database.sql" not in rel_paths
    assert "backup.bak" not in rel_paths
    assert "private.key" not in rel_paths

def test_env_file_exclusions(tmp_path: Path):
    """Verify that .env variations are excluded while .env.example is allowed."""
    (tmp_path / ".env").write_text("SECRET=123")
    (tmp_path / ".env.local").write_text("SECRET=456")
    (tmp_path / ".env.staging").write_text("SECRET=789")
    (tmp_path / ".env.example").write_text("SECRET=REPLACE_ME")
    (tmp_path / "normal.env").write_text("not a real env file")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert ".env.example" in rel_paths
    assert "normal.env" in rel_paths
    assert ".env" not in rel_paths
    assert ".env.local" not in rel_paths
    assert ".env.staging" not in rel_paths
