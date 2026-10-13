#!/usr/bin/env python3
"""Read-only policy checks for Tamanna AI posture archive indexes.
Owner: HM INSAN ALI
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
PROJECT_NAME = "Tamanna AI"
OWNER_NAME = "HM INSAN ALI"
ALLOWED_ENTRY_STATUSES = {
    "STRUCTURE_READ",
    "IDENTITY_MISMATCH",
    "INVALID_JSON_STRUCTURE",
    "UNREADABLE",
}
def check_archive_index(index_path: Path) -> dict:
    if not index_path.is_file():
        raise FileNotFoundError(f"Index not found: {index_path}")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(index, dict):
        raise ValueError("Index must be a JSON object.")
    findings: list[dict] = []
    if index.get("project") != PROJECT_NAME:
        findings.append({
            "code": "PROJECT_MISMATCH",
            "message": "Project name does not match.",
        })
    if index.get("owner") != OWNER_NAME:
        findings.append({
            "code": "OWNER_MISMATCH",
            "message": "Owner does not match.",
        })
    reports = index.get("reports")
    if not isinstance(reports, list):
        findings.append({
            "code": "REPORTS_NOT_LIST",
            "message": "The reports field must be a list.",
        })
        reports = []
    seen_names: set[str] = set()
    for number, entry in enumerate(reports, start=1):
        if not isinstance(entry, dict):
            findings.append({
                "code": "INVALID_ENTRY",
                "entry": number,
                "message": "Entry must be a JSON object.",
            })
            continue
        filename = entry.get("file")
        if (
            not isinstance(filename, str)
            or not filename
            or Path(filename).name != filename
            or filename in {".", ".."}
        ):
            findings.append({
                "code": "INVALID_FILENAME",
                "entry": number,
                "message": "Entry must contain a simple filename.",
            })
        elif filename in seen_names:
            findings.append({
                "code": "DUPLICATE_FILENAME",
                "entry": number,
                "file": filename,
                "message": "Filename appears more than once.",
            })
        else:
            seen_names.add(filename)
        digest = entry.get("sha256")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            findings.append({
                "code": "INVALID_SHA256",
                "entry": number,
                "message": "Entry does not contain a valid lowercase SHA-256 hash.",
            })
        status = entry.get("status")
        if status is not None and status not in ALLOWED_ENTRY_STATUSES:
            findings.append({
                "code": "UNKNOWN_ENTRY_STATUS",
                "entry": number,
                "message": "Entry status is not recognized.",
            })
    return {
        "project": PROJECT_NAME,
        "owner": OWNER_NAME,
        "read_only": True,
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "findings_count": len(findings),
        "findings": findings,
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check policy rules for a posture archive index."
    )
    parser.add_argument("--index", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = check_archive_index(args.index)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == "PASS" else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 2
if __name__ == "__main__":
    raise SystemExit(main())