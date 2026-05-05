
from __future__ import annotations
from pathlib import Path
from llm_context.scanner import scan_directory

def test_security_exclusions(tmp_path: Path):
    """Verify that sensitive files are excluded from scans."""
    (tmp_path / "id_rsa").write_text("private key", encoding="utf-8")
    (tmp_path / "id_ed25519").write_text("private key", encoding="utf-8")
    (tmp_path / "id_rsa.pub").write_text("public key", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=123", encoding="utf-8")
    (tmp_path / ".env.production").write_text("SECRET=456", encoding="utf-8")
    (tmp_path / ".env.example").write_text("SECRET=template", encoding="utf-8")
    (tmp_path / "secret.pem").write_text("cert", encoding="utf-8")
    (tmp_path / "private.key").write_text("key", encoding="utf-8")
    (tmp_path / ".npmrc").write_text("//registry.npmjs.org/:_authToken=XYZ", encoding="utf-8")
    (tmp_path / "normal.py").write_text("print('hello')", encoding="utf-8")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    # Should be excluded
    assert "id_rsa" not in rel_paths
    assert "id_ed25519" not in rel_paths
    assert "id_rsa.pub" not in rel_paths
    assert ".env" not in rel_paths
    assert ".env.production" not in rel_paths
    assert "secret.pem" not in rel_paths
    assert "private.key" not in rel_paths
    assert ".npmrc" not in rel_paths

    # Should be included
    assert "normal.py" in rel_paths
    assert ".env.example" in rel_paths

def test_security_force_include(tmp_path: Path):
    """Verify that force-include can still override security exclusions (use with caution)."""
    (tmp_path / "id_rsa").write_text("private key", encoding="utf-8")

    files = scan_directory(tmp_path, extra_includes=["id_rsa"])
    rel_paths = [f["rel_path"] for f in files]

    assert "id_rsa" in rel_paths
