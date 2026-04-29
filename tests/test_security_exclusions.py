from pathlib import Path
from llm_context.scanner import scan_directory

def test_excludes_sensitive_files(tmp_path: Path):
    # Create sensitive files that SHOULD be excluded
    (tmp_path / ".env.staging").write_text("SECRET=staging")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY")
    (tmp_path / "private.pem").write_text("PEM CONTENT")
    (tmp_path / ".npmrc").write_text("//registry.npmjs.org/:_authToken=XYZ")

    # Create a normal file
    (tmp_path / "main.py").write_text("print('hello')")

    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]

    assert "main.py" in rel_paths
    # These currently FAIL (they ARE included)
    assert ".env.staging" not in rel_paths
    assert "id_rsa" not in rel_paths
    assert "private.pem" not in rel_paths
    assert ".npmrc" not in rel_paths

def test_allows_env_example(tmp_path: Path):
    (tmp_path / ".env.example").write_text("SECRET=your_key_here")
    files = scan_directory(tmp_path)
    rel_paths = [f["rel_path"] for f in files]
    assert ".env.example" in rel_paths
