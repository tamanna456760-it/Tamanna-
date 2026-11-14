"""Validate and restore Tamanna ZIP backups with a dry-run default."""
from __future__ import annotations
import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def inspect_backup(archive_path: str | Path) -> dict[str, Any]:
    path = Path(archive_path)
    with zipfile.ZipFile(path, "r") as archive:
        names = archive.namelist()
        if len(names) > 10000:
            raise ValueError("Backup contains too many entries")
        if len(names) != len(set(names)):
            raise ValueError("Archive contains duplicate entry names")
        if "MANIFEST.json" not in names:
            raise ValueError("Backup manifest is missing")
        try:
            manifest = json.loads(archive.read("MANIFEST.json"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Backup manifest is not valid JSON") from exc
        if not isinstance(manifest, dict):
            raise ValueError("Backup manifest must be a JSON object")
        rows = manifest.get("files")
        if manifest.get("version") != 1 or not isinstance(rows, list):
            raise ValueError("Unsupported or invalid backup manifest")
        listed = set()
        total = 0
        checked = []
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("Invalid backup manifest row")
            name = row.get("path")
            if not isinstance(name, str):
                raise ValueError("Invalid backup path")
            relative = PurePosixPath(name)
            if (relative.is_absolute() or not relative.parts
                    or any(part in {"", ".", ".."} for part in relative.parts)
                    or "\\" in name or ":" in name):
                raise ValueError("Unsafe path in backup")
            if name in listed or name == "MANIFEST.json":
                raise ValueError("Duplicate or reserved path in backup")
            listed.add(name)
            info = archive.getinfo(name)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("Symbolic links are not allowed in backups")
            total += info.file_size
            if info.file_size > 256 * 1024 * 1024 or total > 1024 * 1024 * 1024:
                raise ValueError("Backup exceeds restore size limits")
            if _digest(archive.read(name)) != row.get("sha256"):
                raise ValueError("Checksum mismatch: " + name)
            checked.append(name)
        if set(names) != listed | {"MANIFEST.json"}:
            raise ValueError("Archive contains unmanifested entries")
    return {"status": "valid", "files": checked, "total_bytes": total}

def restore_backup(archive_path: str | Path, destination: str | Path, *, dry_run: bool = True,
                   overwrite: bool = False) -> dict[str, Any]:
    """Validate first. Actual extraction requires explicit dry_run=False."""
    report = inspect_backup(archive_path)
    target = Path(destination).expanduser().resolve()
    with zipfile.ZipFile(archive_path, "r") as archive:
        conflicts = []
        for name in report["files"]:
            output = (target / name).resolve()
            if target not in output.parents:
                raise ValueError("Restore path escapes destination")
            if output.exists():
                conflicts.append(name)
        if conflicts and not overwrite:
            raise FileExistsError("Restore would overwrite: " + ", ".join(conflicts[:5]))
        if dry_run:
            return {**report, "dry_run": True, "destination": str(target), "conflicts": conflicts}
        target.mkdir(parents=True, exist_ok=True)
        for name in report["files"]:
            output = (target / name).resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(archive.read(name))
    return {**report, "dry_run": False, "destination": str(target), "restored": len(report["files"])}

__all__ = ["inspect_backup", "restore_backup"]
