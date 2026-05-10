
import pytest
from pathlib import Path
from llm_context.scanner import scan_directory

def test_security_exclusions(tmp_path):
    """Verify that sensitive files are excluded from scanning."""
    # Setup test files
    (tmp_path / ".env.staging").write_text("SECRET=staging")
    (tmp_path / ".env.example").write_text("SECRET=your_secret_here")
    (tmp_path / "id_rsa").write_text("-----BEGIN RSA PRIVATE KEY-----")
    (tmp_path / "id_ed25519.pub").write_text("ssh-ed25519 AAAAC3...")
    (tmp_path / "private.pem").write_text("-----BEGIN PRIVATE KEY-----")
    (tmp_path / "cert.crt").write_text("-----BEGIN CERTIFICATE-----")
    (tmp_path / "secret.key").write_text("secret_key_content")
    (tmp_path / ".npmrc").write_text("//registry.npmjs.org/:_authToken=XYZ")
    (tmp_path / ".netrc").write_text("machine github.com login user password pass")
    (tmp_path / "public.py").write_text("print('hello')")

    # Run scanner
    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Assertions
    assert "public.py" in rel_paths
    assert ".env.example" in rel_paths

    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "id_ed25519.pub" not in rel_paths
    assert "private.pem" not in rel_paths
    assert "cert.crt" not in rel_paths
    assert "secret.key" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert ".netrc" not in rel_paths

def test_force_include_still_works_for_security_files(tmp_path):
    """Verify that force-include can still override security exclusions if explicitly requested."""
    (tmp_path / ".env.staging").write_text("SECRET=staging")

    # Should be excluded by default
    files = scan_directory(tmp_path)
    assert not any(f["rel_path"] == ".env.staging" for f in files)

    # Should be included if forced
    files = scan_directory(tmp_path, extra_includes=[".env.staging"])
    assert any(f["rel_path"] == ".env.staging" for f in files)
