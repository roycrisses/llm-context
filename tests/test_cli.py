
import pytest
from click.testing import CliRunner
from llm_context.cli import main
import os

def test_cli_default_directory():
    """Verify that DIRECTORY defaults to '.' if not provided."""
    runner = CliRunner()
    # Ensure there's at least one file to avoid "No readable source files found"
    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write("hello world")
        result = runner.invoke(main, ["--ask", "hello"])
        assert result.exit_code == 0
        assert "✨ Included" in result.stderr
        assert "file(s)" in result.stderr

def test_cli_summary_output():
    """Verify that summary information is printed to stderr."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write("hello world")
        result = runner.invoke(main, ["--ask", "hello"])
        assert result.exit_code == 0
        assert "✨ Included" in result.stderr
        assert "tokens" in result.stderr

def test_cli_output_file_summary():
    """Verify summary is included in success message when --output is used."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write("hello world")
        result = runner.invoke(main, ["--ask", "test", "--output", "out.txt"])
        assert result.exit_code == 0
        # success message is sent to stderr by _echo_success
        assert "💾 Context saved to 'out.txt'." in result.stderr
        assert "✨ Included" in result.stderr
        assert "tokens" in result.stderr

def test_cli_detailed_summary():
    """Verify that truncated and omitted counts appear in the summary."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create multiple files
        with open("file1.txt", "w") as f:
            f.write("A" * 1000)
        with open("file2.txt", "w") as f:
            f.write("B" * 1000)
        with open("file3.txt", "w") as f:
            f.write("C" * 1000)

        # Set a very low token limit (e.g., 200 tokens) to force truncation and omission
        # _OVERHEAD_TOKENS is 512, so we need max-tokens > 512 to even start.
        # Let's try 600.
        result = runner.invoke(main, ["--ask", "test", "--max-tokens", "600"])

        assert result.exit_code == 0
        assert "✨ Included" in result.stderr
        # With 600 tokens and 512 overhead, we have ~88 tokens.
        # One file (1000 chars -> ~250 tokens) will be truncated.
        # The other two files will be omitted.
        assert "truncated" in result.stderr
        assert "omitted" in result.stderr
