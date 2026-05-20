"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions
"""

from __future__ import annotations

from pathlib import Path
from llm_context.scanner import scan_directory

def test_security_exclusions(tmp_path: Path):
    """Verify that sensitive files are excluded from scans."""
    # Create various sensitive files
    (tmp_path / ".env.secret").write_text("SECRET=123", encoding="utf-8")
    (tmp_path / ".env.staging").write_text("SECRET=123", encoding="utf-8")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY", encoding="utf-8")
    (tmp_path / "private.pem").write_text("PEM DATA", encoding="utf-8")
    (tmp_path / "db.sql").write_text("DROP TABLE users;", encoding="utf-8")
    (tmp_path / ".npmrc").write_text("_authToken=xyz", encoding="utf-8")
    (tmp_path / ".env.example").write_text("KEY=VALUE", encoding="utf-8") # Should be included
    (tmp_path / "regular.txt").write_text("Hello", encoding="utf-8")       # Should be included

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Should be EXCLUDED
    assert ".env.secret" not in rel_paths
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert "db.sql" not in rel_paths
    assert ".npmrc" not in rel_paths

    # Should be INCLUDED
    assert ".env.example" in rel_paths
    assert "regular.txt" in rel_paths
