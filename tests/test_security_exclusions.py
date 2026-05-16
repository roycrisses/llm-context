"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions
"""

from __future__ import annotations

from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_are_excluded(tmp_path: Path):
    """Verify that sensitive files like SSH keys and .env variants are excluded."""
    (tmp_path / "id_rsa").write_text("private key content", encoding="utf-8")
    (tmp_path / "id_ed25519.pub").write_text("public key content", encoding="utf-8")
    (tmp_path / ".env.staging").write_text("SECRET=staging", encoding="utf-8")
    (tmp_path / "private.pem").write_text("pem content", encoding="utf-8")
    (tmp_path / ".npmrc").write_text("auth token", encoding="utf-8")
    (tmp_path / ".env.example").write_text("API_KEY=your_key_here", encoding="utf-8")
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # These should be EXCLUDED
    assert "id_rsa" not in rel_paths
    assert "id_ed25519.pub" not in rel_paths
    assert ".env.staging" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths

    # These should be INCLUDED
    assert ".env.example" in rel_paths
    assert "main.py" in rel_paths

def test_sensitive_extensions_are_excluded(tmp_path: Path):
    """Verify that files with sensitive extensions are excluded."""
    (tmp_path / "cert.crt").write_text("cert", encoding="utf-8")
    (tmp_path / "key.p12").write_text("p12", encoding="utf-8")
    (tmp_path / "secrets.gpg").write_text("gpg", encoding="utf-8")
    (tmp_path / "safe.py").write_text("safe", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "cert.crt" not in rel_paths
    assert "key.p12" not in rel_paths
    assert "secrets.gpg" not in rel_paths
    assert "safe.py" in rel_paths
