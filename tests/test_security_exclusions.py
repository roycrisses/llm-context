
from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_excluded(tmp_path: Path):
    # Create a dummy project with sensitive files
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / ".env.staging").write_text("STAGING_SECRET=abc")
    (tmp_path / ".env.example").write_text("API_KEY=your_key_here")
    (tmp_path / "id_rsa").write_text("-----BEGIN RSA PRIVATE KEY-----")
    (tmp_path / "private.pem").write_text("-----BEGIN CERTIFICATE-----")
    (tmp_path / ".npmrc").write_text("_auth=hidden")

    files = scan_directory(tmp_path)
    rel_paths = [f['rel_path'] for f in files]

    assert "main.py" in rel_paths
    assert ".env.example" in rel_paths

    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths

def test_extension_exclusions(tmp_path: Path):
    (tmp_path / "cert.crt").write_text("content")
    (tmp_path / "key.key").write_text("content")
    (tmp_path / "archive.gpg").write_text("content")

    files = scan_directory(tmp_path)
    rel_paths = [f['rel_path'] for f in files]

    assert "cert.crt" not in rel_paths
    assert "key.key" not in rel_paths
    assert "archive.gpg" not in rel_paths
