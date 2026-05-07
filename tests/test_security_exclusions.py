"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_are_excluded(tmp_path: Path):
    """
    Ensure that common sensitive files and patterns are excluded by the scanner.
    """
    # Create a variety of sensitive files
    (tmp_path / "id_rsa").write_text("PRIVATE KEY", encoding="utf-8")
    (tmp_path / "id_ed25519").write_text("PRIVATE KEY", encoding="utf-8")
    (tmp_path / ".npmrc").write_text("authToken=123", encoding="utf-8")
    (tmp_path / ".netrc").write_text("machine example.com", encoding="utf-8")
    (tmp_path / ".htpasswd").write_text("user:pass", encoding="utf-8")

    # Files with sensitive extensions
    (tmp_path / "cert.pem").write_text("CERT", encoding="utf-8")
    (tmp_path / "server.key").write_text("KEY", encoding="utf-8")
    (tmp_path / "backup.gpg").write_text("GPG", encoding="utf-8")

    # Various .env patterns
    (tmp_path / ".env.staging").write_text("STAGING=1", encoding="utf-8")
    (tmp_path / ".env.local").write_text("LOCAL=1", encoding="utf-8")

    # Allowed files
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")
    (tmp_path / ".env.example").write_text("TEMPLATE=1", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = {f["rel_path"] for f in files}

    # Verify exclusions
    assert "id_rsa" not in rel_paths
    assert "id_ed25519" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert ".netrc" not in rel_paths
    assert ".htpasswd" not in rel_paths
    assert "cert.pem" not in rel_paths
    assert "server.key" not in rel_paths
    assert "backup.gpg" not in rel_paths
    assert ".env.staging" not in rel_paths
    assert ".env.local" not in rel_paths

    # Verify allowed
    assert "main.py" in rel_paths
    assert ".env.example" in rel_paths
