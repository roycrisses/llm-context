"""
tests/test_security_exclusions.py — Security tests for llm_context.scanner
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from llm_context.scanner import scan_directory


def test_sensitive_files_are_excluded(tmp_path: Path):
    # These are currently NOT excluded (except .env.staging maybe by some coincidence, but likely not)
    (tmp_path / ".env.staging").write_text("SECRET=staging", encoding="utf-8")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY", encoding="utf-8")
    (tmp_path / "private.pem").write_text("PEM CONTENT", encoding="utf-8")
    (tmp_path / ".npmrc").write_text("_auth=abc", encoding="utf-8")
    (tmp_path / "normal.txt").write_text("normal", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # This test is EXPECTED TO FAIL (i.e., find these files) before the fix
    # But wait, Sentinel mission is to fix it.
    # I'll write the test as it SHOULD BE (asserting they ARE excluded)
    # and see it failing first.

    assert "normal.txt" in rel_paths
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths


def test_non_regular_files_are_skipped(tmp_path: Path):
    fifo_path = tmp_path / "my_fifo"
    try:
        os.mkfifo(fifo_path)
    except (AttributeError, OSError):
        pytest.skip("FIFOs not supported on this platform")

    (tmp_path / "normal.txt").write_text("normal", encoding="utf-8")

    # This might hang if scan_directory tries to read the FIFO
    # We'll use a small timeout if possible, or just rely on is_file() fix
    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.txt" in rel_paths
    assert "my_fifo" not in rel_paths
