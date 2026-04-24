import os
import pytest
from llm_context.scanner import scan_directory

def test_excludes_all_env_files_except_example(tmp_path):
    (tmp_path / ".env.secret").write_text("SECRET=123")
    (tmp_path / ".env.staging").write_text("SECRET=456")
    (tmp_path / ".env.example").write_text("SECRET=your_secret_here")
    (tmp_path / ".env").write_text("SECRET=789")
    (tmp_path / "normal.py").write_text("print(1)")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.py" in rel_paths
    assert ".env.example" in rel_paths
    assert ".env" not in rel_paths
    assert ".env.secret" not in rel_paths
    assert ".env.staging" not in rel_paths

def test_excludes_sensitive_extensions(tmp_path):
    (tmp_path / "cert.pem").write_text("-----BEGIN CERTIFICATE-----")
    (tmp_path / "id_rsa.pub").write_text("ssh-rsa ...")
    (tmp_path / "archive.sig").write_text("signature")
    (tmp_path / "normal.txt").write_text("hello")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.txt" in rel_paths
    assert "cert.pem" not in rel_paths
    assert "id_rsa.pub" not in rel_paths
    assert "archive.sig" not in rel_paths

def test_excludes_sensitive_filenames(tmp_path):
    (tmp_path / "id_rsa").write_text("-----BEGIN RSA PRIVATE KEY-----")
    (tmp_path / ".npmrc").write_text("//registry.npmjs.org/:_authToken=...")
    (tmp_path / ".token").write_text("s3cr3t")
    (tmp_path / "normal.md").write_text("# Documentation")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.md" in rel_paths
    assert "id_rsa" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert ".token" not in rel_paths

def test_skips_non_regular_files(tmp_path):
    fifo_path = tmp_path / "test_fifo"
    try:
        os.mkfifo(fifo_path)
    except (AttributeError, OSError):
        pytest.skip("FIFOs not supported on this platform")

    (tmp_path / "normal.py").write_text("print(1)")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "normal.py" in rel_paths
    assert "test_fifo" not in rel_paths
