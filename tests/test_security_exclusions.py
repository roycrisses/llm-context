"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions
"""

from __future__ import annotations

from pathlib import Path
import pytest
from llm_context.scanner import scan_directory

def test_excludes_sensitive_files(tmp_path: Path):
    """Verify that various sensitive files are excluded by default."""
    (tmp_path / ".env.staging").write_text("SECRET=staging", encoding="utf-8")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY", encoding="utf-8")
    (tmp_path / "private.pem").write_text("CERTIFICATE", encoding="utf-8")
    (tmp_path / ".npmrc").write_text("//registry.npmjs.org/:_authToken=...", encoding="utf-8")
    (tmp_path / "normal.txt").write_text("normal", encoding="utf-8")
    (tmp_path / ".env.example").write_text("EXAMPLE=1", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.txt" in rel_paths
    assert ".env.example" in rel_paths
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths

def test_excludes_by_extension(tmp_path: Path):
    """Verify that files with sensitive extensions are excluded."""
    (tmp_path / "cert.crt").write_text("cert")
    (tmp_path / "secret.key").write_text("key")
    (tmp_path / "bundle.p12").write_text("p12")
    (tmp_path / "doc.gpg").write_text("gpg")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "cert.crt" not in rel_paths
    assert "secret.key" not in rel_paths
    assert "bundle.p12" not in rel_paths
    assert "doc.gpg" not in rel_paths

def test_skips_non_regular_files(tmp_path: Path):
    """
    Verify that non-regular files (like FIFOs) are skipped.
    Note: Creating a FIFO might not work on all systems in the same way,
    but we can at least try or rely on the logic if we could mock it.
    In a sandbox environment, we can try mkfifo.
    """
    import os
    fifo_path = tmp_path / "my_fifo"
    try:
        os.mkfifo(fifo_path)
    except (AttributeError, OSError):
        pytest.skip("mkfifo not supported on this system")

    (tmp_path / "normal.txt").write_text("normal")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.txt" in rel_paths
    assert "my_fifo" not in rel_paths
