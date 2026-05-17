"""
tests/test_security_scanner.py — Regression tests for security-related scanner exclusions.
"""

from __future__ import annotations

from pathlib import Path

from llm_context.scanner import scan_directory


def test_excludes_sensitive_extensions(tmp_path: Path):
    (tmp_path / "cert.pem").write_text("PRIVATE KEY")
    (tmp_path / "key.key").write_text("SECRET")
    (tmp_path / "public.pub").write_text("PUBLIC KEY")
    (tmp_path / "normal.txt").write_text("normal")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.txt" in rel_paths
    assert "cert.pem" not in rel_paths
    assert "key.key" not in rel_paths
    assert "public.pub" not in rel_paths


def test_excludes_sensitive_filenames(tmp_path: Path):
    (tmp_path / "id_rsa").write_text("SSH KEY")
    (tmp_path / "id_ed25519").write_text("SSH KEY")
    (tmp_path / ".npmrc").write_text("auth_token=abc")
    (tmp_path / "normal.py").write_text("print(1)")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.py" in rel_paths
    assert "id_rsa" not in rel_paths
    assert "id_ed25519" not in rel_paths
    assert ".npmrc" not in rel_paths


def test_env_file_logic(tmp_path: Path):
    (tmp_path / ".env").write_text("SECRET=1")
    (tmp_path / ".env.test").write_text("SECRET=2")
    (tmp_path / ".env.local").write_text("SECRET=3")
    (tmp_path / ".env.example").write_text("SECRET=template")
    (tmp_path / "normal.py").write_text("print(1)")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.py" in rel_paths
    assert ".env.example" in rel_paths
    assert ".env" not in rel_paths
    assert ".env.test" not in rel_paths
    assert ".env.local" not in rel_paths
