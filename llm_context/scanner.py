"""
scanner.py — Recursively walks a directory, respects .gitignore rules,
filters out noise files, and returns a list of FileInfo dicts.
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Iterator, List, Optional, TypedDict


class FileInfo(TypedDict):
    """Represents a single file discovered by the scanner."""

    path: str  # Absolute path to the file
    rel_path: str  # Path relative to the scanned root
    content: str  # UTF-8 text content (empty string if unreadable)
    size: int  # File size in bytes
    extension: str  # File extension without the dot (e.g. "py")
    mtime: float  # Last-modified timestamp (Unix epoch)


# ---------------------------------------------------------------------------
# Default exclusion rules
# ---------------------------------------------------------------------------

_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        "node_modules",
        "__pycache__",
        ".git",
        ".hg",
        ".svn",
        "dist",
        "build",
        ".venv",
        "venv",
        "env",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "coverage",
        ".next",
        ".nuxt",
        "out",
        ".turbo",
        "vendor",
    }
)

_EXCLUDED_EXTENSIONS: frozenset[str] = frozenset(
    {
        # Binary / media
        "png",
        "jpg",
        "jpeg",
        "gif",
        "bmp",
        "ico",
        "svg",
        "webp",
        "avif",
        "mp4",
        "mov",
        "avi",
        "mkv",
        "webm",
        "mp3",
        "wav",
        "ogg",
        "flac",
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "ppt",
        "pptx",
        "zip",
        "tar",
        "gz",
        "bz2",
        "xz",
        "7z",
        "rar",
        "exe",
        "dll",
        "so",
        "dylib",
        "wasm",
        "ttf",
        "otf",
        "woff",
        "woff2",
        "eot",
        # Secrets / Certificates
        "pem",
        "crt",
        "key",
        "p12",
        "pfx",
        "gpg",
        "pub",
        "sig",
        "asc",
        # Lock / generated
        "lock",
        "map",
        # DB / binary data
        "db",
        "sqlite",
        "sqlite3",
        # Compiled
        "pyc",
        "pyo",
        "class",
    }
)

_EXCLUDED_FILENAMES: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
        ".env.production",
        ".env.development",
        ".DS_Store",
        "Thumbs.db",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "poetry.lock",
        "Pipfile.lock",
        "Cargo.lock",
        "composer.lock",
        "Gemfile.lock",
        ".bash_history",
        ".zsh_history",
        ".history",
        ".python_history",
        ".node_repl_history",
        # SSH Keys
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        # Sensitive config
        ".npmrc",
        ".netrc",
        ".htpasswd",
        ".shsh",
        ".secret",
        ".token",
    }
)


# ---------------------------------------------------------------------------
# .gitignore parser
# ---------------------------------------------------------------------------


def _load_gitignore_patterns(root: Path) -> List[str]:
    """
    Read and return all non-comment, non-empty patterns from a .gitignore
    file located at *root/.gitignore*.  Returns an empty list when no file
    is found.
    """
    gitignore_path = root / ".gitignore"
    if not gitignore_path.is_file():
        return []

    patterns: List[str] = []
    try:
        with gitignore_path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\n")
                # Skip blank lines and comments
                if not line or line.startswith("#"):
                    continue
                # Ignore negation patterns for simplicity (rare edge case)
                if line.startswith("!"):
                    continue
                patterns.append(line)
    except OSError:
        pass

    return patterns


def _matches_gitignore(rel_path: str, patterns: List[str]) -> bool:
    """
    Return True if *rel_path* matches any of the .gitignore *patterns*.
    Uses fnmatch for glob-style matching and also checks plain basename.
    """
    parts = Path(rel_path).parts
    basename = parts[-1] if parts else rel_path

    for pattern in patterns:
        # Strip trailing slash (directory-only marker) for matching
        pat = pattern.rstrip("/")

        # Match against full relative path or just the basename
        if fnmatch.fnmatch(rel_path, pat):
            return True
        if fnmatch.fnmatch(rel_path, f"**/{pat}"):
            return True
        if fnmatch.fnmatch(basename, pat):
            return True

        # Match any path component against directory patterns
        if "/" not in pat:
            for part in parts:
                if fnmatch.fnmatch(part, pat):
                    return True

    return False


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------


def _should_skip_dir(dirname: str) -> bool:
    """Return True if a directory name should be skipped entirely."""
    return dirname in _EXCLUDED_DIRS or dirname.startswith(".")


def _should_skip_file(
    filename: str,
    ext: str,
    rel_path: str,
    gitignore_patterns: List[str],
    extra_excludes: Optional[List[str]],
) -> bool:
    """
    Return True if a file should be excluded from the scan based on:
      - Hardcoded exclusion lists
      - .gitignore patterns
      - User-supplied extra exclusion globs
    """
    if filename in _EXCLUDED_FILENAMES:
        return True
    if ext in _EXCLUDED_EXTENSIONS:
        return True
    # Exclude all .env files except for .env.example
    if filename.startswith(".env") and filename != ".env.example":
        return True
    if _matches_gitignore(rel_path, gitignore_patterns):
        return True
    if extra_excludes:
        for pattern in extra_excludes:
            if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(rel_path, pattern):
                return True
    return False


def _read_file_content(filepath: Path, max_bytes: int = 5_000_000) -> str:
    """
    Attempt to read a file as UTF-8 text.  Returns an empty string when
    the file is binary, unreadable, or exceeds *max_bytes*.
    """
    if filepath.stat().st_size > max_bytes:
        return ""
    try:
        return filepath.read_text(encoding="utf-8", errors="strict")
    except (UnicodeDecodeError, PermissionError, OSError):
        return ""


def _iter_files(
    root: Path,
    gitignore_patterns: List[str],
    extra_includes: Optional[List[str]],
    extra_excludes: Optional[List[str]],
) -> Iterator[FileInfo]:
    """
    Yield :class:`FileInfo` dicts for every qualifying file under *root*.
    """
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        current_dir = Path(dirpath)

        # Prune excluded directories and symbolic links in-place so os.walk won't descend into them
        dirnames[:] = [
            d for d in dirnames if not _should_skip_dir(d) and not (current_dir / d).is_symlink()
        ]

        for filename in filenames:
            filepath = current_dir / filename
            if filepath.is_symlink():
                continue

            try:
                rel_path = str(filepath.relative_to(root))
            except ValueError:
                continue

            ext = filepath.suffix.lstrip(".").lower()

            # Force-include overrides exclusion logic
            force_include = False
            if extra_includes:
                for pattern in extra_includes:
                    if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(rel_path, pattern):
                        force_include = True
                        break

            if not force_include and _should_skip_file(
                filename, ext, rel_path, gitignore_patterns, extra_excludes
            ):
                continue

            try:
                stat = filepath.stat()
            except OSError:
                continue

            content = _read_file_content(filepath)

            yield FileInfo(
                path=str(filepath),
                rel_path=rel_path,
                content=content,
                size=stat.st_size,
                extension=ext,
                mtime=stat.st_mtime,
            )


def scan_directory(
    root: str | Path,
    extra_includes: Optional[List[str]] = None,
    extra_excludes: Optional[List[str]] = None,
) -> List[FileInfo]:
    """
    Recursively scan *root* and return a list of :class:`FileInfo` dicts
    for every non-excluded text file found.

    Parameters
    ----------
    root:
        The directory to scan.
    extra_includes:
        Optional list of glob patterns for files to force-include even if
        they would ordinarily be excluded.
    extra_excludes:
        Optional list of glob patterns for files to exclude in addition to
        the built-in exclusion list.

    Returns
    -------
    List[FileInfo]
        Discovered files, ordered by relative path.

    Raises
    ------
    FileNotFoundError
        When *root* does not exist.
    NotADirectoryError
        When *root* is not a directory.
    """
    root = Path(root).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    gitignore_patterns = _load_gitignore_patterns(root)

    files = list(_iter_files(root, gitignore_patterns, extra_includes, extra_excludes))

    # Stable sort by relative path
    files.sort(key=lambda f: f["rel_path"])
    return files
