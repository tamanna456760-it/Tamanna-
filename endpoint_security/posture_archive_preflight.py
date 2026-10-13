#!/usr/bin/env python3
"""Read-only preflight checks for Tamanna AI posture archives.
Owner: HM INSAN ALI
This module validates an archive index before verification.
It does not modify or delete reports.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
ALLOWED_ENTRY_STATUSES = {
    "STRUCTURE_READ",
    "IDENTITY_MISMATCH",
    "INVALID_JSON_STRUCTURE",
    "UNREADABLE",
}
def preflight_archive(index_path: str | Path) -> dict[str, Any]:
    """Return a read-only validation result for an archive index."""
    path = Path(index_path)
    findings: list[str] = []
    if not path.exists():
        return {
            "project": PROJECT,
            "owner": OWNER,
            "status": "REVIEW_REQUIRED",
            "findings": ["INDEX_NOT_FOUND"],
            "read_only": True,
        }
    if path.is_symlink() or not path.is_file():
        return {
            "project": PROJECT,
            "owner": OWNER,
            "status": "REVIEW_REQUIRED",
            "findings": ["INDEX_NOT_A_REGULAR_FILE"],
            "read_only": True,
        }
    try:
        with path.open("r", encoding="utf-8") as handle:
            index = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {
            "project": PROJECT,
            "owner": OWNER,
            "status": "REVIEW_REQUIRED",
            "findings": ["INDEX_UNREADABLE_OR_INVALID_JSON"],
            "read_only": True,
        }
    if not isinstance(index, dict):
        return {
            "project": PROJECT,
            "owner": OWNER,
            "status": "REVIEW_REQUIRED",
            "findings": ["INDEX_ROOT_MUST_BE_OBJECT"],
            "read_only": True,
        }
    if index.get("project") != PROJECT:
        findings.append("PROJECT_MISMATCH")
    if index.get("owner") != OWNER:
        findings.append("OWNER_MISMATCH")
    reports = index.get("reports")
    if not isinstance(reports, list):
        findings.append("REPORTS_MUST_BE_LIST")
        reports = []
    seen_names: set[str] = set()
    for position, entry in enumerate(reports):
        prefix = f"REPORT_{position}"
        if not isinstance(entry, dict):
            findings.append(f"{prefix}_MUST_BE_OBJECT")
            continue
        filename = entry.get("filename")
        if not isinstance(filename, str) or not filename:
            findings.append(f"{prefix}_INVALID_FILENAME")
        else:
            candidate = Path(filename)
            if (
                candidate.is_absolute()
                or candidate.name != filename
                or filename in {".", ".."}
                or "/" in filename
                or "\\" in filename
            ):
                findings.append(f"{prefix}_UNSAFE_FILENAME")
            if filename in seen_names:
                findings.append(f"{prefix}_DUPLICATE_FILENAME")
            seen_names.add(filename)
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
            findings.append(f"{prefix}_INVALID_SHA256")
        status = entry.get("status")
        if status not in ALLOWED_ENTRY_STATUSES:
            findings.append(f"{prefix}_UNKNOWN_STATUS")
    return {
        "project": PROJECT,
        "owner": OWNER,
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "findings": findings,
        "report_count": len(reports),
        "read_only": True,
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run read-only Tamanna AI posture archive preflight checks."
    )
    parser.add_argument(
        "--index",
        required=True,
        help="Path to the posture archive index JSON file",
    )
    args = parser.parse_args()
    result = preflight_archive(args.index)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1
if __name__ == "__main__":
    raise SystemExit(main())