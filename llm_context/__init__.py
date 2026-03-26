"""
llm-context: Analyze any codebase, find the most relevant files to your
question, trim to fit the LLM's token limit, and output a ready-to-use
context block.
"""

__version__ = "0.1.0"
__author__ = "llm-context contributors"
__license__ = "MIT"

from llm_context.scanner import scan_directory, FileInfo
from llm_context.ranker import rank_files
from llm_context.trimmer import trim_to_budget
from llm_context.context import build_context_block

__all__ = [
    "scan_directory",
    "FileInfo",
    "rank_files",
    "trim_to_budget",
    "build_context_block",
]
