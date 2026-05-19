from pathlib import Path
from llm_context.scanner import scan_directory

def test_security_exclusions(tmp_path):
    # Sensitive filenames
    (tmp_path / "id_rsa").write_text("private")
    (tmp_path / "id_ed25519").write_text("private")
    (tmp_path / ".npmrc").write_text("token=123")

    # Sensitive extensions
    (tmp_path / "cert.pem").write_text("cert")
    (tmp_path / "db.sql").write_text("dump")
    (tmp_path / "backup.bak").write_text("backup")

    # .env patterns
    (tmp_path / ".env").write_text("secret")
    (tmp_path / ".env.staging").write_text("secret")
    (tmp_path / ".env.example").write_text("not-a-secret")

    # Normal file
    (tmp_path / "app.py").write_text("print(1)")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Assert exclusions
    assert "id_rsa" not in rel_paths
    assert "id_ed25519" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert "cert.pem" not in rel_paths
    assert "db.sql" not in rel_paths
    assert "backup.bak" not in rel_paths
    assert ".env" not in rel_paths
    assert ".env.staging" not in rel_paths

    # Assert inclusions
    assert "app.py" in rel_paths
    assert ".env.example" in rel_paths
