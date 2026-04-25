from pathlib import Path
from llm_context.scanner import scan_directory

def test_sensitive_files_excluded(tmp_path: Path):
    # Create sensitive files
    (tmp_path / ".env.secret").write_text("SECRET=123")
    (tmp_path / "id_rsa").write_text("SSH KEY")
    (tmp_path / "cert.pem").write_text("PEM")
    (tmp_path / "key.crt").write_text("CRT")
    (tmp_path / ".npmrc").write_text("token=abc")
    (tmp_path / ".secret").write_text("shhh")
    (tmp_path / "token.gpg").write_text("gpg")

    # Create normal files
    (tmp_path / "main.py").write_text("print(1)")
    (tmp_path / ".env.example").write_text("SECRET=")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "main.py" in rel_paths
    assert ".env.example" in rel_paths

    assert ".env.secret" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "cert.pem" not in rel_paths
    assert "key.crt" not in rel_paths
    assert ".npmrc" not in rel_paths
    assert ".secret" not in rel_paths
    assert "token.gpg" not in rel_paths

def test_env_files_behavior(tmp_path: Path):
    (tmp_path / ".env").write_text("x")
    (tmp_path / ".env.local").write_text("x")
    (tmp_path / ".env.production").write_text("x")
    (tmp_path / ".env.example").write_text("x")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert ".env.example" in rel_paths
    assert ".env" not in rel_paths
    assert ".env.local" not in rel_paths
    assert ".env.production" not in rel_paths

def test_ssh_keys_excluded(tmp_path: Path):
    (tmp_path / "id_rsa").write_text("x")
    (tmp_path / "id_dsa").write_text("x")
    (tmp_path / "id_ecdsa").write_text("x")
    (tmp_path / "id_ed25519").write_text("x")
    (tmp_path / "id_rsa.pub").write_text("x")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "id_rsa" not in rel_paths
    assert "id_dsa" not in rel_paths
    assert "id_ecdsa" not in rel_paths
    assert "id_ed25519" not in rel_paths
    assert "id_rsa.pub" not in rel_paths # .pub is in excluded extensions
