"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_file_exclusions(tmp_path: Path):
    """Verify that sensitive files are excluded from scans."""
    (tmp_path / ".env.staging").write_text("SECRET=staging_secret")
    (tmp_path / "id_rsa").write_text("SSH KEY")
    (tmp_path / "private.pem").write_text("PEM CONTENT")
    (tmp_path / ".npmrc").write_text("//registry.npmjs.org/:_authToken=SECRET")
    (tmp_path / ".env.example").write_text("SECRET=your_secret_here")
    (tmp_path / "regular.py").write_text("print('hello')")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Should be excluded
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths

    # Should be included
    assert ".env.example" in rel_paths
    assert "regular.py" in rel_paths
