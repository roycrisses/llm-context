"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_are_excluded(tmp_path: Path):
    """Ensure that known sensitive files and extensions are never included in the scan."""
    # Create a project with sensitive files
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")

    # Sensitive files to exclude
    sensitive_files = [
        ".env",
        ".env.staging",
        ".env.local",
        "id_rsa",
        "id_ed25519",
        ".npmrc",
        ".netrc",
        "private.key",
        "cert.pem",
        "secrets.gpg"
    ]

    for f in sensitive_files:
        (tmp_path / f).write_text("secret content")

    # .env.example SHOULD be included
    (tmp_path / ".env.example").write_text("API_KEY=your_key_here")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Check that sensitive files are NOT in the results
    for f in sensitive_files:
        assert f not in rel_paths, f"{f} should have been excluded but was found in results."

    # Check that allowed files ARE in the results
    assert "src/main.py" in rel_paths
    assert ".env.example" in rel_paths
