#!/usr/bin/env python3
"""Read-only summary of existing Tamanna AI Endpoint Security reports."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_NAME = "Tamanna AI"
OWNER = "HM INSAN ALI"
DEFAULT_REPORT_DIR = Path("data/security_audits")


def load_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Report root must be a JSON object.")
    if data.get("project") != PROJECT_NAME:
        raise ValueError("Report belongs to a different project.")
    return data


def summarize_reports(report_dir: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "project": PROJECT_NAME, "owner": OWNER,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "NO_REPORTS", "reports_found": 0, "reports_read": 0,
        "reports_invalid": 0, "checks_passed": 0, "checks_failed": 0,
        "checks_error": 0, "reports": [], "read_only": True,
    }
    if not report_dir.is_dir():
        summary["status"] = "REPORT_DIRECTORY_MISSING"
        return summary
    report_paths = sorted(path for path in report_dir.glob("*.json") if path.is_file())
    summary["reports_found"] = len(report_paths)
    for path in report_paths:
        entry: dict[str, Any] = {"file": path.name, "status": "INVALID"}
        try:
            report = load_report(path)
            entry["status"] = str(report.get("status", "UNKNOWN"))
            entry["audit_time_utc"] = report.get("audit_time_utc")
            entry["summary"] = report.get("summary", {})
            checks = report.get("checks", [])
            if isinstance(checks, list):
                for check in checks:
                    if not isinstance(check, dict):
                        summary["checks_error"] += 1
                        continue
                    check_status = str(check.get("status", "ERROR")).upper()
                    if check_status in {"PASS", "PASSED", "OK"}:
                        summary["checks_passed"] += 1
                    elif check_status in {"FAIL", "FAILED"}:
                        summary["checks_failed"] += 1
                    else:
                        summary["checks_error"] += 1
            summary["reports_read"] += 1
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            summary["reports_invalid"] += 1
        summary["reports"].append(entry)
    if summary["reports_invalid"] or summary["checks_failed"] or summary["checks_error"]:
        summary["status"] = "REVIEW_REQUIRED"
    elif summary["reports_read"]:
        summary["status"] = "REPORTS_READ"
    else:
        summary["status"] = "NO_REPORTS"
    summary["note"] = "This summarizes existing JSON reports only; it does not run scans or prove system security."
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a read-only Tamanna AI security posture summary.")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = summarize_reports(args.report_dir)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(rendered + "\n")
        except FileExistsError:
            print(f"ERROR: Output already exists: {args.output}")
            return 2
        except OSError as exc:
            print(f"ERROR: Cannot write report: {exc}")
            return 2
    print(rendered)
    return 1 if result["status"] == "REVIEW_REQUIRED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
