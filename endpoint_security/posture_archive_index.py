#!/usr/bin/env python3
"""Build a read-only index of Tamanna AI posture report files.
Owner: HM INSAN ALI
This module inventories report files. It does not certify their authenticity
or independently prove that the underlying security checks were performed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
PROJECT_NAME = "Tamanna AI"
OWNER_NAME = "HM INSAN ALI"
DEFAULT_REPORT_DIR = Path("data/security_audits")
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
def index_reports(report_dir: Path) -> dict:
    entries: list[dict] = []
    unreadable_count = 0
    if not report_dir.is_dir():
        return {
            "project": PROJECT_NAME,
            "owner": OWNER_NAME,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "REPORT_DIRECTORY_MISSING",
            "read_only": True,
            "reports_found": 0,
            "reports_unreadable": 0,
            "reports": [],
        }
    for path in sorted(report_dir.glob("*.json")):
        if not path.is_file() or path.is_symlink():
            continue
        entry = {
            "file": path.name,
            "status": "UNVERIFIED",
            "sha256": None,
            "report_status": "UNKNOWN",
            "schema_validation": "NOT_CHECKED",
        }
        try:
            raw = path.read_bytes()
            parsed = json.loads(raw.decode("utf-8"))
            entry["sha256"] = hashlib.sha256(raw).hexdigest()
            if isinstance(parsed, dict):
                entry["report_status"] = parsed.get("status", "UNKNOWN")
                entry["project_matches"] = (
                    parsed.get("project") == PROJECT_NAME
                )
                entry["owner_matches"] = (
                    parsed.get("owner") == OWNER_NAME
                )
                entry["status"] = (
                    "STRUCTURE_READ"
                    if entry["project_matches"] and entry["owner_matches"]
                    else "IDENTITY_MISMATCH"
                )
            else:
                entry["status"] = "INVALID_JSON_STRUCTURE"
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            unreadable_count += 1
            entry["status"] = "UNREADABLE"
        entries.append(entry)
    return {
        "project": PROJECT_NAME,
        "owner": OWNER_NAME,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "REPORTS_INDEXED" if entries else "NO_REPORTS",
        "read_only": True,
        "reports_found": len(entries),
        "reports_unreadable": unreadable_count,
        "reports": entries,
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a read-only index of posture reports."
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=DEFAULT_REPORT_DIR,
        help="Directory containing JSON reports.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New output JSON path; existing files are never overwritten.",
    )
    args = parser.parse_args()
    try:
        index = index_reports(args.report_dir)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as file:
            json.dump(index, file, indent=2, ensure_ascii=False)
            file.write("\n")
        print(json.dumps({
            "status": index["status"],
            "reports_found": index["reports_found"],
            "reports_unreadable": index["reports_unreadable"],
            "output": str(args.output),
            "read_only": True,
        }, indent=2))
        return 0 if index["status"] == "REPORTS_INDEXED" else 1
    except FileExistsError:
        print("ERROR: Output file already exists; choose another path.")
        return 2
    except OSError as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 2
if __name__ == "__main__":
    raise SystemExit(main())