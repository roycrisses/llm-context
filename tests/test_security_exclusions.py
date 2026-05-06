"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions
"""

from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_excluded(tmp_path: Path):
    """Ensure various sensitive files are excluded from scanning."""
    # Create a mix of sensitive and normal files
    (tmp_path / ".env.staging").write_text("SECRET=staging")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY")
    (tmp_path / "private.pem").write_text("PEM CONTENT")
    (tmp_path / ".npmrc").write_text("auth_token=xyz")
    (tmp_path / "normal.py").write_text("print('hello')")
    (tmp_path / ".env.example").write_text("VAR=placeholder")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Sensitive files should be EXCLUDED
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths

    # Normal and example files should be INCLUDED
    assert "normal.py" in rel_paths
    assert ".env.example" in rel_paths

def test_more_security_extensions_excluded(tmp_path: Path):
    """Verify additional security-related extensions are excluded."""
    extensions = ["crt", "key", "p12", "pfx", "gpg", "pub", "sig", "asc"]
    for ext in extensions:
        (tmp_path / f"test.{ext}").write_text("secret content")

    (tmp_path / "test.txt").write_text("safe content")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    for ext in extensions:
        assert f"test.{ext}" not in rel_paths

    assert "test.txt" in rel_paths
