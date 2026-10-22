#!/usr/bin/env python3
"""
Tamanna AI — Production Readiness Report
Owner: HM INSAN ALI
Summarizes supplied deployment check JSON reports.
Read-only: does not deploy or modify services.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
def load_report(path):
    with Path(path).open("r", encoding="utf-8") as file:
        report = json.load(file)
    if not isinstance(report, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return report
def build_readiness_report(report_paths):
    findings = []
    checks = []
    for report_path in report_paths:
        try:
            report = load_report(report_path)
        except (OSError, json.JSONDecodeError, UnicodeError, ValueError) as exc:
            findings.append(f"Cannot read {report_path}: {exc}")
            checks.append({
                "source": str(report_path),
                "status": "ERROR",
            })
            continue
        if report.get("project") != PROJECT:
            findings.append(f"{report_path}: project mismatch")
        if report.get("owner") != OWNER:
            findings.append(f"{report_path}: owner mismatch")
        status = report.get("status")
        if status != "PASS":
            findings.append(f"{report_path}: status is not PASS")
        checks.append({
            "source": str(report_path),
            "status": status if isinstance(status, str) else "INVALID",
            "findings_count": (
                len(report["findings"])
                if isinstance(report.get("findings"), list)
                else None
            ),
        })
    all_passed = bool(checks) and not findings
    return {
        "project": PROJECT,
        "owner": OWNER,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all_passed else "REVIEW_REQUIRED",
        "checks": checks,
        "findings": findings,
        "read_only": True,
        "note": (
            "Summarizes supplied JSON reports only. Does not independently "
            "verify the server, DNS, TLS connection, or deployment."
        ),
    }
def main():
    parser = argparse.ArgumentParser(
        description="Build a Tamanna AI production readiness report."
    )
    parser.add_argument(
        "reports",
        nargs="+",
        help="Paths to existing deployment check JSON reports",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="New output JSON path; existing files are not overwritten",
    )
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        parser.error("Output file already exists; choose a new path")
    report = build_readiness_report(args.reports)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open("x", encoding="utf-8") as file:
            json.dump(report, file, indent=2, ensure_ascii=False)
            file.write("\n")
    except OSError as exc:
        parser.error(f"Cannot write report: {exc}")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
if __name__ == "__main__":
    main()