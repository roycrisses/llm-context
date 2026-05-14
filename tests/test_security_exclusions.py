"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_are_excluded(tmp_path: Path):
    """Verify that common sensitive files are automatically excluded from scans."""
    (tmp_path / "id_rsa").write_text("PRIVATE KEY")
    (tmp_path / "id_ed25519.pub").write_text("PUBLIC KEY")
    (tmp_path / ".env.staging").write_text("SECRET=123")
    (tmp_path / ".env.production").write_text("SECRET=456")
    (tmp_path / ".env.example").write_text("KEY=VALUE")
    (tmp_path / "cert.pem").write_text("CERT")
    (tmp_path / "private.key").write_text("KEY")
    (tmp_path / ".npmrc").write_text("registry=...")
    (tmp_path / "safe.txt").write_text("SAFE")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # These should be excluded
    assert "id_rsa" not in rel_paths
    assert "id_ed25519.pub" not in rel_paths
    assert ".env.staging" not in rel_paths
    assert ".env.production" not in rel_paths
    assert "cert.pem" not in rel_paths
    assert "private.key" not in rel_paths
    assert ".npmrc" not in rel_paths

    # These should be included
    assert "safe.txt" in rel_paths
    assert ".env.example" in rel_paths
