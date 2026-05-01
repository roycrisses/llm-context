
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
        assert "Included" in result.stderr
        assert "file(s)" in result.stderr

def test_cli_summary_output():
    """Verify that summary information is printed to stderr."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write("hello world")
        result = runner.invoke(main, ["--ask", "hello"])
        assert result.exit_code == 0
        assert "Included" in result.stderr
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
        assert "Context saved to 'out.txt'." in result.stderr
        assert "Included" in result.stderr
        assert "tokens" in result.stderr
