
#!/usr/bin/env python3
"""
Tamanna AI — Boot Integrity Engine
Version: v1.0.1-ADVANCED
Owner: HM INSAN ALI

Features:
- SHA-256 file hashing
- Manifest integrity verification
- Safe path validation
- Read-only verification by default
- No automatic file deletion or modification
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

VERSION = "v1.0.1-ADVANCED"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "core" / "boot_manifest.json"

logger = logging.getLogger("tamanna.integrity")


class IntegrityError(RuntimeError):
    """Raised when integrity verification fails."""


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 without loading the whole file into memory."""
    digest = hashlib.sha256()

    with file_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _safe_project_path(relative_path: str) -> Path:
    """Reject absolute paths and paths escaping the project directory."""
    candidate = Path(relative_path)

    if candidate.is_absolute() or ".." in candidate.parts:
        raise IntegrityError(f"Unsafe relative path: {relative_path}")

    root = PROJECT_ROOT.resolve()
    target = (root / candidate).resolve()

    if not target.is_relative_to(root):
        raise IntegrityError(f"Path escapes project root: {relative_path}")

    return target


def load_manifest() -> dict[str, Any]:
    """Read and validate the manifest structure."""
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise IntegrityError("Boot manifest is missing") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError("Cannot read a valid boot manifest") from exc

    if not isinstance(data, dict):
        raise IntegrityError("Manifest must be a JSON object")

    integrity = data.get("integrity")
    if not isinstance(integrity, dict):
        raise IntegrityError("Manifest integrity section is missing")

    if integrity.get("algorithm") != "sha256":
        raise IntegrityError("Unsupported integrity algorithm")

    return data


def verify_files(
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Verify files against recorded hashes.
    Empty records are treated as unconfigured, never as a pass.
    """
    manifest = manifest if manifest is not None else load_manifest()
    records = manifest.get("integrity", {}).get("files")

    if not isinstance(records, dict) or not records:
        return {
            "ok": False,
            "status": "NOT_CONFIGURED",
            "verified": 0,
            "failures": ["No SHA-256 records configured"],
        }

    verified: list[str] = []
    failures: list[str] = []

    for relative_path, expected_hash in records.items():
        try:
            if not isinstance(relative_path, str):
                raise IntegrityError("Manifest path must be a string")

            if (
                not isinstance(expected_hash, str)
                or len(expected_hash) != 64
                or any(ch not in "0123456789abcdef"
                       for ch in expected_hash.lower())
            ):
                raise IntegrityError(f"Invalid SHA-256: {relative_path}")

            target = _safe_project_path(relative_path)

            if not target.is_file():
                raise IntegrityError(f"File not found: {relative_path}")

            actual_hash = calculate_sha256(target)

            if actual_hash.lower() != expected_hash.lower():
                raise IntegrityError(f"Hash mismatch: {relative_path}")

            verified.append(relative_path)

        except (IntegrityError, OSError) as exc:
            failures.append(str(exc))

    success = not failures and bool(verified)

    return {
        "ok": success,
        "status": "VERIFIED" if success else "FAILED",
        "verified": len(verified),
        "failures": failures,
    }


def create_hash_records(
    relative_paths: list[str],
) -> dict[str, str]:
    """
    Calculate hashes for explicitly selected existing project files.
    This returns records; it does not modify the manifest.
    """
    if not relative_paths:
        raise IntegrityError("Select at least one file")

    records: dict[str, str] = {}

    for relative_path in relative_paths:
        target = _safe_project_path(relative_path)

        if not target.is_file():
            raise IntegrityError(f"File not found: {relative_path}")

        records[relative_path] = calculate_sha256(target)

    return records


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        result = verify_files()
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if not result["ok"]:
            raise SystemExit(1)

    except IntegrityError as exc:
        logger.error("Integrity check could not run: %s", exc)
        raise SystemExit(1)
