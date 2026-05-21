
import pytest
from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_file_exclusions(tmp_path):
    # Setup test files
    (tmp_path / "id_rsa").write_text("private key")
    (tmp_path / "id_ecdsa").write_text("private key")
    (tmp_path / "id_ed25519").write_text("private key")
    (tmp_path / ".npmrc").write_text("npm config")
    (tmp_path / ".netrc").write_text("netrc config")
    (tmp_path / ".htpasswd").write_text("htpasswd")

    (tmp_path / "cert.pem").write_text("cert")
    (tmp_path / "server.crt").write_text("cert")
    (tmp_path / "db.key").write_text("key")
    (tmp_path / "secret.gpg").write_text("gpg")

    (tmp_path / "backup.sql").write_text("sql")
    (tmp_path / "db.bak").write_text("bak")
    (tmp_path / "data.dump").write_text("dump")

    (tmp_path / ".env.staging").write_text("env staging")
    (tmp_path / ".env.production.local").write_text("env prod local")
    (tmp_path / ".env.example").write_text("env example")

    (tmp_path / "normal.py").write_text("print('hello')")

    # Run scan
    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Assert exclusions
    assert "id_rsa" not in rel_paths
    assert "id_ecdsa" not in rel_paths
    assert "id_ed25519" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert ".netrc" not in rel_paths
    assert ".htpasswd" not in rel_paths

    assert "cert.pem" not in rel_paths
    assert "server.crt" not in rel_paths
    assert "db.key" not in rel_paths
    assert "secret.gpg" not in rel_paths

    assert "backup.sql" not in rel_paths
    assert "db.bak" not in rel_paths
    assert "data.dump" not in rel_paths

    assert ".env.staging" not in rel_paths
    assert ".env.production.local" not in rel_paths

    # Assert inclusions
    assert "normal.py" in rel_paths
    assert ".env.example" in rel_paths
