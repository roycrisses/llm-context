
import shutil
from pathlib import Path
import pytest
from llm_context.scanner import scan_directory

@pytest.fixture
def test_dir(tmp_path):
    d = tmp_path / "test_scan"
    d.mkdir()
    return d

def test_security_exclusions(test_dir):
    # Files that should be excluded
    (test_dir / ".env.staging").write_text("SECRET=123")
    (test_dir / "id_rsa").write_text("PRIVATE KEY")
    (test_dir / ".npmrc").write_text("auth")
    (test_dir / "database.sql").write_text("SELECT * FROM users")
    (test_dir / "cert.pem").write_text("CERTIFICATE")
    (test_dir / "secret.key").write_text("KEY")
    (test_dir / ".htpasswd").write_text("user:pass")

    # Files that should be included
    (test_dir / "regular.py").write_text("print('hello')")
    (test_dir / ".env.example").write_text("SECRET=template")

    files = scan_directory(test_dir)
    rel_paths = {f["rel_path"] for f in files}

    # Check exclusions
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert "database.sql" not in rel_paths
    assert "cert.pem" not in rel_paths
    assert "secret.key" not in rel_paths
    assert ".htpasswd" not in rel_paths

    # Check inclusions
    assert "regular.py" in rel_paths
    assert ".env.example" in rel_paths
