
from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_excluded(tmp_path: Path):
    """Verify that sensitive files and extensions are correctly excluded."""
    # SSH keys
    (tmp_path / "id_rsa").write_text("PRIVATE KEY")
    (tmp_path / "id_ed25519").write_text("PRIVATE KEY")

    # Config files with credentials
    (tmp_path / ".npmrc").write_text("_auth=token")
    (tmp_path / ".netrc").write_text("machine github.com")
    (tmp_path / ".htpasswd").write_text("user:hash")

    # Security extensions
    (tmp_path / "cert.pem").write_text("CERTIFICATE")
    (tmp_path / "server.key").write_text("KEY")
    (tmp_path / "root.crt").write_text("CERTIFICATE")

    # DB/Backup extensions
    (tmp_path / "backup.sql").write_text("SQL")
    (tmp_path / "data.bak").write_text("BAK")
    (tmp_path / "db.dump").write_text("DUMP")

    # Env files
    (tmp_path / ".env.staging").write_text("SECRET=123")
    (tmp_path / ".env.local").write_text("SECRET=456")
    (tmp_path / ".env.example").write_text("SECRET=YOUR_KEY")

    # Normal file
    (tmp_path / "app.py").write_text("print('hello')")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Check exclusions
    assert "id_rsa" not in rel_paths
    assert "id_ed25519" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert ".netrc" not in rel_paths
    assert ".htpasswd" not in rel_paths
    assert "cert.pem" not in rel_paths
    assert "server.key" not in rel_paths
    assert "root.crt" not in rel_paths
    assert "backup.sql" not in rel_paths
    assert "data.bak" not in rel_paths
    assert "db.dump" not in rel_paths
    assert ".env.staging" not in rel_paths
    assert ".env.local" not in rel_paths

    # Check inclusions
    assert "app.py" in rel_paths
    assert ".env.example" in rel_paths
