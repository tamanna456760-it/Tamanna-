"""Bounded, read-only project context and chat response formatting."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build",
    ".tamanna_backup", ".tamanna",
}
EXCLUDED_NAMES = {
    ".env", ".env.local", ".env.production", "id_rsa",
    "id_ed25519", "credentials.json",
}
SUPPORTED_SUFFIXES = {
    ".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml",
    ".ini", ".js", ".ts", ".tsx", ".html", ".css",
}
MAX_FILES = 1500
MAX_FILE_BYTES = 64_000
MAX_CONTEXT_FILES = 8
MAX_CONTEXT_CHARS = 16_000


def _safe_root(root: str | Path) -> Path:
    path = Path(root).expanduser().resolve()
    if not path.is_dir():
        raise NotADirectoryError(str(path))
    return path


def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS or part.startswith(".env") for part in path.parts)


def build_project_context(root: str | Path, query: str = "") -> dict[str, Any]:
    """Return a small, read-only set of text files relevant to a query."""
    project_root = _safe_root(root)
    terms = {
        token.casefold()
        for token in re.findall(r"[\w.-]{2,}", str(query))
        if token.casefold() not in {"the", "and", "for", "with", "this", "that"}
    }

    candidates: list[tuple[int, str, str]] = []
    scanned = 0
    skipped = 0

    for current, directories, filenames in os.walk(project_root, followlinks=False):
        directories[:] = sorted(
            name for name in directories
            if name not in EXCLUDED_DIRS and not name.startswith(".")
        )
        for filename in sorted(filenames):
            if scanned >= MAX_FILES:
                break
            relative = (Path(current) / filename).relative_to(project_root)
            if _is_excluded(relative) or filename in EXCLUDED_NAMES:
                skipped += 1
                continue
            path = project_root / relative
            if path.is_symlink() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            scanned += 1
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    skipped += 1
                    continue
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                skipped += 1
                continue

            rel = relative.as_posix()
            haystack = (rel + "\n" + text[:4000]).casefold()
            score = sum(1 for term in terms if term in haystack)
            if not terms or score:
                candidates.append((score, rel, text[:MAX_FILE_BYTES]))

        if scanned >= MAX_FILES:
            break

    candidates.sort(key=lambda item: (-item[0], item[1].casefold()))
    selected = []
    used = 0
    for score, rel, text in candidates[:MAX_CONTEXT_FILES]:
        chunk = text[: max(0, MAX_CONTEXT_CHARS - used)]
        if not chunk:
            break
        selected.append({
            "path": rel,
            "score": score,
            "content": chunk,
        })
        used += len(chunk)
        if used >= MAX_CONTEXT_CHARS:
            break

    return {
        "project_root": str(project_root),
        "total_files": scanned,
        "relevant_files": selected,
        "truncated": scanned >= MAX_FILES or len(candidates) > MAX_CONTEXT_FILES,
        "skipped_files": skipped,
    }


def format_response(result: Any, message: str) -> dict[str, Any]:
    """Normalize a model/module result into the stable chat response shape."""
    if isinstance(result, dict):
        payload = dict(result)
        reply = next(
            (
                payload.get(key)
                for key in ("reply", "response", "answer", "text", "content", "message")
                if isinstance(payload.get(key), str) and payload.get(key).strip()
            ),
            "",
        )
        payload.setdefault("ok", bool(reply))
        payload.setdefault("type", "chat")
        payload["reply"] = reply
        payload.setdefault("source", "tamanna_ai")
        payload.setdefault("input", message)
        return payload

    reply = "" if result is None else str(result)
    return {
        "ok": bool(reply.strip()),
        "type": "chat",
        "reply": reply,
        "source": "tamanna_ai",
        "input": message,
    }


__all__ = ["build_project_context", "format_response"]
