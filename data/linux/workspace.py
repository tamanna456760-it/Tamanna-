"""Confined project workspace operations for Tamanna AI.

All paths are relative to the repository root. Writes are admin-only at the API
layer; this module also blocks traversal, symlink escapes, secrets and .git.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_TEXT_BYTES = 512_000
BLOCKED_PARTS = {".git", ".env", ".ssh", ".aws", ".config", "__pycache__"}


class WorkspaceError(ValueError):
    pass


def resolve(relative: str, *, allow_missing: bool = False) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise WorkspaceError("A relative project path is required.")
    candidate = Path(relative)
    if candidate.is_absolute() or "\x00" in relative:
        raise WorkspaceError("Absolute paths and NUL bytes are not allowed.")
    if any(part in BLOCKED_PARTS or part.startswith(".env.") for part in candidate.parts):
        raise WorkspaceError("This protected path cannot be accessed.")
    target = (ROOT / candidate).resolve(strict=not allow_missing)
    try:
        target.relative_to(ROOT)
    except ValueError as exc:
        raise WorkspaceError("Path escapes the project workspace.") from exc
    if any(part in BLOCKED_PARTS or part.startswith(".env.") for part in target.relative_to(ROOT).parts):
        raise WorkspaceError("This protected path cannot be accessed.")
    return target


def operate(action: str, path: str = "", destination: str = "", content: str = "") -> dict:
    action = str(action).lower().strip()
    if action == "list" and not str(path or "").strip():
        path = "."
    target = resolve(path, allow_missing=action in {"write", "mkdir", "move"})
    if action in {"write", "mkdir", "move", "remove"} and target == ROOT:
        raise WorkspaceError("The project root itself cannot be modified or removed.")
    if action == "list":
        if not target.is_dir():
            raise WorkspaceError("Path is not a directory.")
        items = []
        for child in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))[:300]:
            if child.name in BLOCKED_PARTS or child.name.startswith(".env."):
                continue
            items.append({"name": child.name, "type": "directory" if child.is_dir() else "file"})
        return {"ok": True, "path": path or ".", "items": items}
    if action == "read":
        if not target.is_file():
            raise WorkspaceError("File does not exist.")
        if target.stat().st_size > MAX_TEXT_BYTES:
            raise WorkspaceError("File exceeds the 512 KB text limit.")
        try:
            data = target.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise WorkspaceError("Binary or non-UTF-8 files are not supported.") from exc
        return {"ok": True, "path": path, "content": data}
    if action == "write":
        if not isinstance(content, str) or len(content.encode("utf-8")) > MAX_TEXT_BYTES:
            raise WorkspaceError("Content must be UTF-8 text no larger than 512 KB.")
        target.parent.mkdir(parents=True, exist_ok=True)
        # Re-check after creating parent directories to prevent symlink escapes.
        target = resolve(path, allow_missing=True)
        fd, temp_name = tempfile.mkstemp(prefix=".tamanna-", dir=str(target.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        return {"ok": True, "action": "write", "path": path, "bytes": target.stat().st_size}
    if action == "mkdir":
        target.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "action": action, "path": path}
    if action == "move":
        dest = resolve(destination, allow_missing=True)
        if not target.exists():
            raise WorkspaceError("Source path does not exist.")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest = resolve(destination, allow_missing=True)
        if dest.exists():
            raise WorkspaceError("Destination already exists; refusing to overwrite.")
        shutil.move(str(target), str(dest))
        return {"ok": True, "action": action, "from": path, "to": destination}
    if action == "remove":
        if not target.exists():
            raise WorkspaceError("Path does not exist.")
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        return {"ok": True, "action": action, "path": path}
    raise WorkspaceError("Supported actions: list, read, write, mkdir, move, remove.")
