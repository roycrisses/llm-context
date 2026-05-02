"""
tests/test_security_exclusions.py — Regression tests for sensitive file exclusions.
"""

from __future__ import annotations

from llm_context.scanner import _should_skip_file

def test_env_files_exclusion():
    # Standard .env files should be excluded
    assert _should_skip_file(".env", "", ".env", [], None) is True
    assert _should_skip_file(".env.local", "", ".env.local", [], None) is True

    # Custom .env files should also be excluded by the new logic
    assert _should_skip_file(".env.staging", "staging", ".env.staging", [], None) is True
    assert _should_skip_file(".env.test.local", "local", ".env.test.local", [], None) is True

    # .env.example should NOT be excluded
    assert _should_skip_file(".env.example", "example", ".env.example", [], None) is False

def test_ssh_keys_exclusion():
    assert _should_skip_file("id_rsa", "", "id_rsa", [], None) is True
    assert _should_skip_file("id_ed25519", "", "id_ed25519", [], None) is True
    # id_rsa.pub should be excluded by extension
    assert _should_skip_file("id_rsa.pub", "pub", "id_rsa.pub", [], None) is True

def test_sensitive_configs_exclusion():
    assert _should_skip_file(".npmrc", "npmrc", ".npmrc", [], None) is True
    assert _should_skip_file(".netrc", "netrc", ".netrc", [], None) is True
    assert _should_skip_file(".secret", "secret", ".secret", [], None) is True

def test_secret_extensions_exclusion():
    assert _should_skip_file("private.pem", "pem", "private.pem", [], None) is True
    assert _should_skip_file("cert.crt", "crt", "cert.crt", [], None) is True
    assert _should_skip_file("archive.gpg", "gpg", "archive.gpg", [], None) is True
    assert _should_skip_file("dummy.key", "key", "dummy.key", [], None) is True
