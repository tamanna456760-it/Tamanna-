"""Local book-library synchronization helpers for Tamanna AI.

The repository does not define a remote source-of-truth for books. This module
therefore provides a safe local inventory step until that provider is configured.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def _books_directory() -> Path:
    # TODO: Confirm the canonical library path when the remote book provider is chosen.
    configured = os.getenv("TAMANNA_BOOKS_DIR")
    return Path(configured).expanduser() if configured else Path(__file__).resolve().parents[1] / "data" / "books"


def sync_books() -> dict[str, Any]:
    """Ensure the local books directory exists and return its file inventory."""
    directory = _books_directory().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in directory.rglob("*") if path.is_file())
    return {
        "status": "ok",
        "directory": str(directory),
        "synced": len(files),
        "files": [str(path.relative_to(directory)) for path in files[:500]],
        "truncated": len(files) > 500,
    }


__all__ = ["sync_books"]
