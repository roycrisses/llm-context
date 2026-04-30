"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from pathlib import Path

from llm_context.scanner import scan_directory


def test_excludes_various_env_files(tmp_path: Path):
    """Verify that all .env variants except .env.example are excluded."""
    (tmp_path / ".env").write_text("SECRET=123")
    (tmp_path / ".env.local").write_text("SECRET=123")
    (tmp_path / ".env.staging").write_text("SECRET=123")
    (tmp_path / ".env.example").write_text("SECRET=your_secret_here")
    (tmp_path / "normal.py").write_text("print('hello')")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.py" in rel_paths
    assert ".env.example" in rel_paths
    assert ".env" not in rel_paths
    assert ".env.local" not in rel_paths
    assert ".env.staging" not in rel_paths


def test_excludes_sensitive_filenames(tmp_path: Path):
    """Verify that common sensitive filenames are excluded."""
    (tmp_path / "id_rsa").write_text("PRIVATE KEY")
    (tmp_path / ".npmrc").write_text("authToken=123")
    (tmp_path / ".htpasswd").write_text("user:pass")
    (tmp_path / "main.py").write_text("pass")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "main.py" in rel_paths
    assert "id_rsa" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert ".htpasswd" not in rel_paths


def test_excludes_sensitive_extensions(tmp_path: Path):
    """Verify that common sensitive extensions are excluded."""
    (tmp_path / "cert.pem").write_text("CERT")
    (tmp_path / "key.key").write_text("KEY")
    (tmp_path / "secret.gpg").write_bytes(b"\x85\x01\x02")
    (tmp_path / "public.pub").write_text("ssh-rsa ...")
    (tmp_path / "script.sh").write_text("echo hi")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "script.sh" in rel_paths
    assert "cert.pem" not in rel_paths
    assert "key.key" not in rel_paths
    assert "secret.gpg" not in rel_paths
    assert "public.pub" not in rel_paths
