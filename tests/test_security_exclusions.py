
from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_file_exclusions(tmp_path: Path):
    """Verify that sensitive files and extensions are excluded from scans."""
    # Create a mix of sensitive and normal files
    (tmp_path / ".env.staging").write_text("SECRET=staging")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY")
    (tmp_path / "private.pem").write_text("PEM")
    (tmp_path / ".npmrc").write_text("AUTH")
    (tmp_path / "backup.sql").write_text("DUMP")
    (tmp_path / "normal.py").write_text("print(1)")
    (tmp_path / ".env.example").write_text("KEY=VALUE")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # These should be excluded
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert "backup.sql" not in rel_paths

    # These should be included
    assert "normal.py" in rel_paths
    assert ".env.example" in rel_paths

def test_ssh_key_patterns(tmp_path: Path):
    """Verify various SSH key filename patterns are excluded."""
    keys = ["id_rsa", "id_ecdsa", "id_ecdsa_sk", "id_ed25519", "id_ed25519_sk", "id_dsa"]
    for key in keys:
        (tmp_path / key).write_text("key content")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    for key in keys:
        assert key not in rel_paths

def test_sensitive_extensions(tmp_path: Path):
    """Verify various sensitive extensions are excluded."""
    exts = ["pem", "crt", "key", "p12", "pfx", "gpg", "pub", "sig", "asc", "sql", "bak", "dump"]
    for ext in exts:
        (tmp_path / f"file.{ext}").write_text("content")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    for ext in exts:
        assert f"file.{ext}" not in rel_paths
