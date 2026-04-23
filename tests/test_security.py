
import os
from pathlib import Path
import pytest
from llm_context.scanner import scan_directory

def test_fifo_is_skipped(tmp_path):
    """Verify that FIFOs are skipped and do not cause a hang."""
    fifo_path = tmp_path / "test_fifo"
    os.mkfifo(fifo_path)

    # scan_directory should return an empty list because the only file is a FIFO
    files = scan_directory(tmp_path)
    assert len(files) == 0

def test_sensitive_files_are_skipped(tmp_path):
    """Verify that sensitive files like SSH keys and .env files are skipped."""
    (tmp_path / "id_rsa").write_text("private key")
    (tmp_path / ".npmrc").write_text("npm config")
    (tmp_path / ".env").write_text("SECRET=123")
    (tmp_path / ".env.local").write_text("SECRET=456")
    (tmp_path / ".env.example").write_text("SECRET=YOUR_KEY")
    (tmp_path / "regular.py").write_text("print('hello')")

    files = scan_directory(tmp_path)
    filenames = [f["rel_path"] for f in files]

    assert "regular.py" in filenames
    assert ".env.example" in filenames
    assert "id_rsa" not in filenames
    assert ".npmrc" not in filenames
    assert ".env" not in filenames
    assert ".env.local" not in filenames

def test_sensitive_extensions_are_skipped(tmp_path):
    """Verify that sensitive extensions like .pem, .crt, .key are skipped."""
    (tmp_path / "cert.pem").write_text("cert")
    (tmp_path / "cert.crt").write_text("cert")
    (tmp_path / "server.key").write_text("key")
    (tmp_path / "id_rsa.pub").write_text("public key")
    (tmp_path / "secret.gpg").write_text("encrypted")

    files = scan_directory(tmp_path)
    assert len(files) == 0
