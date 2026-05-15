"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions
"""

from __future__ import annotations

from pathlib import Path
import pytest
from llm_context.scanner import scan_directory

def test_sensitive_files_are_excluded(tmp_path: Path):
    # Create sensitive files
    (tmp_path / ".env.staging").write_text("SECRET_KEY=leak")
    (tmp_path / "id_rsa").write_text("-----BEGIN RSA PRIVATE KEY-----")
    (tmp_path / "private.pem").write_text("-----BEGIN PRIVATE KEY-----")
    (tmp_path / ".npmrc").write_text("//registry.npmjs.org/:_authToken=token")
    (tmp_path / "safe.txt").write_text("safe content")
    (tmp_path / ".env.example").write_text("API_KEY=your_key_here")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # These should be excluded
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths

    # These should be included
    assert "safe.txt" in rel_paths
    assert ".env.example" in rel_paths
