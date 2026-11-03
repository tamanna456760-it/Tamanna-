"""Build a conservative, read-only summary of a posture archive result."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EXPECTED_PROJECT = "Tamanna AI"
EXPECTED_OWNER = "HM INSAN ALI"


def _review(findings: list[str], *, project: Any = EXPECTED_PROJECT, owner: Any = EXPECTED_OWNER) -> dict[str, Any]:
    return {
        "project": project,
        "owner": owner,
        "status": "REVIEW_REQUIRED",
        "validation": "INVALID",
        "read_only": True,
        "findings": list(dict.fromkeys(findings)),
    }


def build_summary(result_path: str | Path) -> dict[str, Any]:
    """Load a validator JSON result and return PASS only for trusted valid data.

    The function does not modify the supplied file. Any missing, malformed,
    unexpected, or mismatched data is reported as REVIEW_REQUIRED.
    """
    path = Path(result_path)
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return _review(["RESULT_FILE_NOT_FOUND_OR_UNSAFE"])

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError):
        return _review(["RESULT_FILE_INVALID"])

    if not isinstance(data, dict):
        return _review(["RESULT_ROOT_NOT_OBJECT"])

    findings_value = data.get("findings", [])
    findings: list[str] = []
    if not isinstance(findings_value, list) or any(not isinstance(item, str) for item in findings_value):
        findings.append("RESULT_FINDINGS_INVALID")
        if isinstance(findings_value, list):
            findings.extend(item for item in findings_value if isinstance(item, str))
    else:
        findings.extend(findings_value)

    project = data.get("project")
    owner = data.get("owner")
    if project != EXPECTED_PROJECT or owner != EXPECTED_OWNER:
        findings.append("PROJECT_OR_OWNER_MISMATCH")
    if data.get("validation") != "VALID":
        # Preserve source findings (for example SCHEMA_ERROR) and force review.
        findings.append("VALIDATION_NOT_VALID")
    if data.get("status") != "PASS":
        findings.append("RESULT_STATUS_NOT_PASS")
    if data.get("read_only") is not True:
        findings.append("READ_ONLY_NOT_CONFIRMED")

    normalized = list(dict.fromkeys(findings))
    status = "PASS" if not normalized else "REVIEW_REQUIRED"
    return {
        "project": project,
        "owner": owner,
        "status": status,
        "validation": data.get("validation"),
        "read_only": data.get("read_only") is True,
        "findings": normalized,
    }


__all__ = ["build_summary"]
