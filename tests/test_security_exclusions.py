
from pathlib import Path
import pytest
from llm_context.scanner import scan_directory

def test_sensitive_file_exclusions(tmp_path: Path):
    """Verify that sensitive files are excluded from scanning."""
    # Create sensitive files
    sensitive_files = [
        ".env.staging",
        ".env.local",
        "id_rsa",
        "id_ed25519.pub",  # .pub extension is in _EXCLUDED_EXTENSIONS
        "private.pem",
        ".npmrc",
        "backup.sql",
        "config.bak",
        "data.dump",
        "secret.key",
        "cert.crt",
        "vault.gpg",
    ]

    for f in sensitive_files:
        (tmp_path / f).write_text("sensitive data")

    # Create allowed files
    allowed_files = [
        "main.py",
        "README.md",
        ".env.example",
    ]

    for f in allowed_files:
        (tmp_path / f).write_text("public data")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Check that sensitive files are NOT present
    for f in sensitive_files:
        assert f not in rel_paths, f"Sensitive file {f} was leaked!"

    # Check that allowed files ARE present
    for f in allowed_files:
        assert f in rel_paths, f"Allowed file {f} was missing!"

def test_env_prefix_exclusion(tmp_path: Path):
    """Verify that all .env* files except .env.example are excluded."""
    env_files = [
        ".env",
        ".env.production",
        ".env.qa",
        ".env.anything",
    ]

    for f in env_files:
        (tmp_path / f).write_text("secret")

    (tmp_path / ".env.example").write_text("public")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    for f in env_files:
        assert f not in rel_paths, f"Sensitive env file {f} was leaked!"

    assert ".env.example" in rel_paths
