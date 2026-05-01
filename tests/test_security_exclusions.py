"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from pathlib import Path
import pytest
from llm_context.scanner import scan_directory

@pytest.fixture()
def sensitive_project(tmp_path: Path) -> Path:
    """Create a project with various sensitive files."""
    # Credential files
    (tmp_path / ".npmrc").write_text("auth=token")
    (tmp_path / ".netrc").write_text("machine host login user password pass")
    (tmp_path / ".htpasswd").write_text("user:hashedpass")

    # Environment files
    (tmp_path / ".env").write_text("SECRET=123")
    (tmp_path / ".env.staging").write_text("SECRET=456")
    (tmp_path / ".env.example").write_text("SECRET=")

    # SSH keys
    (tmp_path / "id_rsa").write_text("PRIVATE KEY")
    (tmp_path / "id_ed25519").write_text("PRIVATE KEY")
    (tmp_path / "id_rsa.pub").write_text("PUBLIC KEY")

    # Certs and keys
    (tmp_path / "server.key").write_text("KEY")
    (tmp_path / "server.crt").write_text("CERT")
    (tmp_path / "private.pem").write_text("PEM")

    # Normal files
    (tmp_path / "app.py").write_text("print('hi')")
    (tmp_path / "README.md").write_text("# Readme")

    return tmp_path

def test_sensitive_files_are_excluded(sensitive_project: Path):
    """Verify that sensitive files are excluded while non-sensitive ones are kept."""
    files = scan_directory(sensitive_project)
    rel_paths = [f["rel_path"] for f in files]

    # Should be INCLUDED
    assert "app.py" in rel_paths
    assert "README.md" in rel_paths
    assert ".env.example" in rel_paths

    # Should be EXCLUDED
    assert ".npmrc" not in rel_paths
    assert ".netrc" not in rel_paths
    assert ".htpasswd" not in rel_paths
    assert ".env" not in rel_paths
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "id_ed25519" not in rel_paths
    assert "id_rsa.pub" not in rel_paths
    assert "server.key" not in rel_paths
    assert "server.crt" not in rel_paths
    assert "private.pem" not in rel_paths

def test_force_include_overrides_security_exclusion(sensitive_project: Path):
    """Verify that extra_includes can still force-include excluded files if the user insists."""
    files = scan_directory(sensitive_project, extra_includes=[".env.staging", "server.key"])
    rel_paths = [f["rel_path"] for f in files]

    assert ".env.staging" in rel_paths
    assert "server.key" in rel_paths
    assert ".env" not in rel_paths # Still excluded
