#!/usr/bin/env python3
"""Read-only audit dashboard summary for Tamanna AI.
Owner: HM INSAN ALI
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
DEFAULT_REPORT_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "security_audits"
)
def load_report(path: Path) -> dict:
    """Load one JSON report and return its basic audit information."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Report root must be a JSON object.")
    if data.get("project") != "Tamanna AI":
        raise ValueError("Unexpected project name.")
    summary = data.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("Missing or invalid summary.")
    return {
        "file": path.name,
        "audit_time_utc": data.get("audit_time_utc", "unknown"),
        "overall_status": summary.get("overall_status", "UNKNOWN"),
        "total": summary.get("total", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "errors": summary.get("errors", 0),
    }
def build_dashboard(report_dir: Path) -> dict:
    """Summarize available JSON reports without modifying them."""
    reports = []
    invalid_reports = []
    if not report_dir.is_dir():
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "report_count": 0,
            "reports": [],
            "invalid_reports": [],
            "message": f"Report directory not found: {report_dir}",
        }
    for path in sorted(report_dir.glob("*.json")):
        try:
            reports.append(load_report(path))
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            invalid_reports.append({
                "file": path.name,
                "error": f"{type(exc).__name__}: {exc}",
            })
    reports.sort(
        key=lambda item: item["audit_time_utc"],
        reverse=True,
    )
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "report_count": len(reports),
        "invalid_report_count": len(invalid_reports),
        "latest_report": reports[0] if reports else None,
        "totals": {
            "passed": sum(item["passed"] for item in reports),
            "failed": sum(item["failed"] for item in reports),
            "errors": sum(item["errors"] for item in reports),
        },
        "reports": reports,
        "invalid_reports": invalid_reports,
        "note": (
            "Summary of report contents only. It does not independently "
            "verify report authenticity or prove the system is malware-free."
        ),
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Show Tamanna AI security audit report summaries."
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=DEFAULT_REPORT_DIR,
        help="Directory containing JSON audit reports.",
    )
    args = parser.parse_args()
    dashboard = build_dashboard(args.report_dir)
    print(json.dumps(dashboard, indent=2))
    return 1 if dashboard.get("invalid_report_count", 0) else 0
if __name__ == "__main__":
    raise SystemExit(main())