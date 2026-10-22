
#!/usr/bin/env python3
"""
Tamanna AI — Core Boot Manager
Version: v1.0.1-ADVANCED
Build: MASTER-SYNC
Owner: HM INSAN ALI

Safe boot orchestration and integrity verification.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any

VERSION = "v1.0.1-ADVANCED"
SYSTEM_NAME = "TAMANNA SYSTEM"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = CORE_DIR / "boot_manifest.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TAMANNA-BOOT] %(levelname)s %(message)s",
)
logger = logging.getLogger("tamanna.boot")


BOOT_STAGES = (
    "initialize-zero-state",
    "load-identity",
    "activate-dual-engine",
    "sync-heartbeat-loop",
    "engage-ficar-power",
    "link-powerhub",
    "verify-integrity",
    "system-online",
)


class BootError(RuntimeError):
    """Raised when a required boot stage fails."""


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def load_manifest() -> dict[str, Any]:
    """Load the boot manifest without executing its contents."""
    if not MANIFEST_PATH.is_file():
        raise BootError(
            f"Boot manifest not found: {MANIFEST_PATH}"
        )

    try:
        manifest = json.loads(
            MANIFEST_PATH.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise BootError("Boot manifest is unreadable or invalid") from exc

    if not isinstance(manifest, dict):
        raise BootError("Manifest root must be a JSON object")

    if manifest.get("version") != VERSION:
        raise BootError("Manifest version mismatch")

    return manifest


def verify_integrity(manifest: dict[str, Any]) -> None:
    """
    Verify files listed in the manifest against their expected SHA-256.

    Expected manifest format:
    {
      "version": "v1.0.1-ADVANCED",
      "files": {
        "core/boot_manager.py": "<64-character SHA-256>"
      }
    }
    """
    files = manifest.get("files")

    if not isinstance(files, dict) or not files:
        raise BootError("No integrity records configured")

    for relative_name, expected_hash in files.items():
        relative_path = Path(relative_name)

        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise BootError(f"Unsafe manifest path: {relative_name}")

        target = (PROJECT_ROOT / relative_path).resolve()

        if not target.is_relative_to(PROJECT_ROOT.resolve()):
            raise BootError(f"Path escapes project root: {relative_name}")

        if not target.is_file():
            raise BootError(f"Integrity target missing: {relative_name}")

        if (
            not isinstance(expected_hash, str)
            or len(expected_hash) != 64
            or any(c not in "0123456789abcdef" for c in expected_hash.lower())
        ):
            raise BootError(f"Invalid SHA-256 record: {relative_name}")

        actual_hash = sha256_file(target)

        if actual_hash.lower() != expected_hash.lower():
            raise BootError(f"Integrity mismatch: {relative_name}")

        logger.info("Integrity verified: %s", relative_name)


def run_boot_checks() -> dict[str, Any]:
    """Run safe checks; do not start unconfigured external services."""
    completed: list[str] = []

    try:
        logger.info("%s — %s", SYSTEM_NAME, VERSION)

        # Stage 0: initialize boot state
        completed.append(BOOT_STAGES[0])

        # Stage 1: load declared identity
        manifest = load_manifest()
        identity = manifest.get("identity", {})
        if not isinstance(identity, dict):
            raise BootError("Invalid identity section")
        completed.append(BOOT_STAGES[1])

        # Stages 2–5 require real engine/service integrations.
        # Do not pretend these are active when not configured.
        pending = list(BOOT_STAGES[2:6])

        # Stage 6: verify integrity before reporting ready.
        verify_integrity(manifest)
        completed.append(BOOT_STAGES[6])

        # Stage 7 is deliberately not marked online:
        # engine and service integrations are still pending.
        return {
            "system": SYSTEM_NAME,
            "version": VERSION,
            "identity": identity,
            "status": "CHECKS_PASSED_INTEGRATIONS_PENDING",
            "completed_stages": completed,
            "pending_stages": pending + [BOOT_STAGES[7]],
        }

    except (BootError, OSError) as exc:
        logger.error("Boot checks failed: %s", exc)
        return {
            "system": SYSTEM_NAME,
            "version": VERSION,
            "status": "BOOT_BLOCKED",
            "completed_stages": completed,
            "error": str(exc),
        }


if __name__ == "__main__":
    result = run_boot_checks()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result["status"] != "CHECKS_PASSED_INTEGRATIONS_PENDING":
        raise SystemExit(1)
