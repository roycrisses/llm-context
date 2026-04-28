"""
tests/test_security_exclusions.py — Security-focused tests for scanner exclusions
"""
from __future__ import annotations
from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_are_excluded(tmp_path: Path):
    # Sensitive files that SHOULD be excluded
    (tmp_path / ".env.staging").write_text("SECRET=staging")
    (tmp_path / "id_rsa").write_text("-----BEGIN RSA PRIVATE KEY-----")
    (tmp_path / "private.pem").write_text("-----BEGIN RSA PRIVATE KEY-----")
    (tmp_path / ".npmrc").write_text("//registry.npmjs.org/:_authToken=SECRET")

    # Files that SHOULD be included
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / ".env.example").write_text("SECRET=your_secret_here")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # These assertions are expected to FAIL before the fix
    assert ".env.staging" not in rel_paths, f".env.staging should be excluded but was found in {rel_paths}"
    assert "id_rsa" not in rel_paths, f"id_rsa should be excluded but was found in {rel_paths}"
    assert "private.pem" not in rel_paths, f"private.pem should be excluded but was found in {rel_paths}"
    assert ".npmrc" not in rel_paths, f".npmrc should be excluded but was found in {rel_paths}"

    # These should always pass
    assert "main.py" in rel_paths
    assert ".env.example" in rel_paths
