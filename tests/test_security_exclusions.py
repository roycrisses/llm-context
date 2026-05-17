"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from pathlib import Path
import pytest
from llm_context.scanner import scan_directory

def test_sensitive_files_are_excluded(tmp_path: Path):
    # Create various sensitive files
    (tmp_path / "id_rsa").write_text("private key")
    (tmp_path / "id_ed25519.pub").write_text("public key")
    (tmp_path / ".npmrc").write_text("auth_token=abc")
    (tmp_path / "private.pem").write_text("pem content")
    (tmp_path / "server.key").write_text("key content")
    (tmp_path / ".env.staging").write_text("SECRET=123")
    (tmp_path / "backup.sql").write_text("DROP TABLE users;")
    (tmp_path / "data.dump").write_text("binary dump")

    # Create normal files
    (tmp_path / "app.py").write_text("print('hello')")
    (tmp_path / ".env.example").write_text("PORT=3000")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Verify exclusions
    assert "id_rsa" not in rel_paths
    assert "id_ed25519.pub" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert "private.pem" not in rel_paths
    assert "server.key" not in rel_paths
    assert ".env.staging" not in rel_paths
    assert "backup.sql" not in rel_paths
    assert "data.dump" not in rel_paths

    # Verify inclusions
    assert "app.py" in rel_paths
    assert ".env.example" in rel_paths

def test_extra_include_can_override_security_exclusions(tmp_path: Path):
    (tmp_path / ".env.staging").write_text("SECRET=123")

    # Normally excluded
    files = scan_directory(tmp_path)
    assert not any(f["rel_path"] == ".env.staging" for f in files)

    # Forced include
    files = scan_directory(tmp_path, extra_includes=[".env.staging"])
    assert any(f["rel_path"] == ".env.staging" for f in files)
