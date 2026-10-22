
#!/usr/bin/env python3
"""
Tamanna AI — Core Identity Manager
Version: v1.0.1-ADVANCED
Build: MASTER-SYNC
Owner: HM INSAN ALI

Purpose:
- Load system identity from boot_manifest.json
- Validate required identity fields
- Report identity status
- Never modify or delete project files
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

VERSION = "v1.0.1-ADVANCED"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "core" / "boot_manifest.json"

logger = logging.getLogger("tamanna.identity")


class IdentityError(RuntimeError):
    """Raised when the system identity is invalid."""


def read_manifest() -> dict[str, Any]:
    """Read the identity source from the boot manifest."""
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise IdentityError("boot_manifest.json is missing") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise IdentityError("Cannot read boot manifest") from exc

    if not isinstance(data, dict):
        raise IdentityError("Manifest must be a JSON object")

    return data


def load_identity() -> dict[str, str]:
    """Load and validate the canonical Tamanna system identity."""
    manifest = read_manifest()
    identity = manifest.get("identity")

    if not isinstance(identity, dict):
        raise IdentityError("Identity section is missing")

    required = {
        "name": "Tamanna AI",
        "system_id": None,
        "environment": None,
    }

    for key, expected in required.items():
        value = identity.get(key)

        if not isinstance(value, str) or not value.strip():
            raise IdentityError(f"Missing or invalid identity field: {key}")

        if expected is not None and value != expected:
            raise IdentityError(f"Unexpected identity value: {key}")

    if manifest.get("system") != "TAMANNA SYSTEM":
        raise IdentityError("System name mismatch")

    if manifest.get("version") != VERSION:
        raise IdentityError("System version mismatch")

    if manifest.get("build_type") != "MASTER-SYNC":
        raise IdentityError("Build type mismatch")

    result = {
        "system": manifest["system"],
        "name": identity["name"],
        "system_id": identity["system_id"],
        "version": manifest["version"],
        "build_type": manifest["build_type"],
        "environment": identity["environment"],
        "status": "IDENTITY_VALID",
    }

    logger.info(
        "Identity validated: %s (%s)",
        result["name"],
        result["version"],
    )

    return result


def identity_status() -> dict[str, Any]:
    """Return a machine-readable identity check result."""
    try:
        return {
            "ok": True,
            "identity": load_identity(),
        }
    except (IdentityError, OSError) as exc:
        logger.error("Identity validation failed: %s", exc)
        return {
            "ok": False,
            "status": "IDENTITY_INVALID",
            "error": str(exc),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    result = identity_status()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if not result["ok"]:
        raise SystemExit(1)
