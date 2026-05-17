
from pathlib import Path
from llm_context.scanner import scan_directory

def test_security_exclusions(tmp_path: Path):
    """Verify that sensitive files and extensions are excluded from scans."""

    # 1. Test .env patterns
    (tmp_path / ".env.staging").write_text("SECRET=123")
    (tmp_path / ".env.local").write_text("SECRET=123")
    (tmp_path / ".env").write_text("SECRET=123")
    (tmp_path / ".env.example").write_text("SECRET=") # Should NOT be excluded

    # 2. Test SSH keys
    (tmp_path / "id_rsa").write_text("---BEGIN RSA PRIVATE KEY---")
    (tmp_path / "id_ed25519.pub").write_text("ssh-ed25519 ...")

    # 3. Test sensitive extensions
    (tmp_path / "cert.pem").write_text("cert")
    (tmp_path / "db.sql").write_text("CREATE TABLE...")

    # 4. Test other sensitive files
    (tmp_path / ".npmrc").write_text("auth_token=...")

    # 5. Public file
    (tmp_path / "README.md").write_text("# Hello")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Assertions
    assert "README.md" in rel_paths
    assert ".env.example" in rel_paths

    assert ".env" not in rel_paths
    assert ".env.staging" not in rel_paths
    assert ".env.local" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "id_ed25519.pub" not in rel_paths
    assert "cert.pem" not in rel_paths
    assert "db.sql" not in rel_paths
    assert ".npmrc" not in rel_paths
