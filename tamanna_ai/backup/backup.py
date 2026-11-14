"""Verified ZIP backup creation for user-selected files and directories."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import zipfile
from pathlib import Path

_EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", "node_modules"}
_EXCLUDED_NAMES = {".env", ".env.local", ".env.production"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_backup(source: str | Path, destination: str | Path) -> dict[str, object]:
    """Create an archive; secret env files and symlinks are intentionally skipped."""
    src = Path(source).expanduser().resolve()
    dest = Path(destination).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(src)
    if src.is_symlink():
        raise ValueError("Backup source cannot be a symbolic link")
    if dest.exists():
        raise FileExistsError(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if src.is_file():
        candidates = [src]
        base = src.parent
    else:
        base = src
        candidates = sorted(p for p in src.rglob("*") if p.is_file())

    rows: list[dict[str, str]] = []
    try:
        with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in candidates:
                if path.is_symlink() or _EXCLUDED_NAMES.intersection(path.parts):
                    continue
                if _EXCLUDED_PARTS.intersection(path.parts):
                    continue
                relative = path.relative_to(base).as_posix()
                if relative == dest.name or relative.startswith("../"):
                    continue
                archive.write(path, relative)
                rows.append({"path": relative, "sha256": _sha256(path)})
            archive.writestr(
                "MANIFEST.json",
                json.dumps({"version": 1, "files": rows}, ensure_ascii=False, indent=2),
            )
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    return {"status": "ok", "archive": str(dest), "files": len(rows), "manifest": "MANIFEST.json"}


__all__ = ["create_backup"]
