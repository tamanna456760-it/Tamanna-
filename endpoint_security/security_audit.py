#!/usr/bin/env python3
"""Read-only security audit runner for Tamanna AI.
Owner: HM INSAN ALI
This script reports checks; it does not enforce security actions.
"""
from __future__ import annotations
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from endpoint_security.config_validator import validate_config
from endpoint_security.policy_checker import check_policy
ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "endpoint_security" / "endpoint_config.json"
REPORT_DIR = ROOT / "data" / "security_audits"
def run_check(name, function):
    try:
        result = function()
        passed = bool(result.get("valid", result.get("healthy", False)))
        return {
            "check": name,
            "status": "PASS" if passed else "FAIL",
            "details": result,
        }
    except Exception as exc:
        return {
            "check": name,
            "status": "ERROR",
            "details": f"{type(exc).__name__}: {exc}",
        }
def check_unit_tests():
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(ROOT / "endpoint_security" / "tests"),
            "-p",
            "test_*.py",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return {
        "valid": completed.returncode == 0,
        "return_code": completed.returncode,
        "stdout": completed.stdout[-8000:],
        "stderr": completed.stderr[-8000:],
    }
def main():
    checks = [
        run_check(
            "configuration",
            lambda: validate_config(CONFIG),
        ),
        run_check(
            "security_policy",
            lambda: check_policy(CONFIG),
        ),
        run_check(
            "unit_tests",
            check_unit_tests,
        ),
    ]
    passed = sum(item["status"] == "PASS" for item in checks)
    failed = sum(item["status"] == "FAIL" for item in checks)
    errors = sum(item["status"] == "ERROR" for item in checks)
    report = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "audit_time_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "read_only",
        "summary": {
            "total": len(checks),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "overall_status": (
                "PASS"
                if passed == len(checks)
                else "REVIEW_REQUIRED"
            ),
        },
        "checks": checks,
        "limitations": [
            "A passing report does not prove the system is malware-free.",
            "Network security and live process enforcement are not tested.",
            "File integrity is not checked unless a separate baseline scan is configured.",
        ],
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / (
        "security-audit-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + ".json"
    )
    # Exclusive creation avoids overwriting an existing report.
    with report_path.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report["summary"], indent=2))
    print(f"Report saved: {report_path.relative_to(ROOT)}")
    return 0 if report["summary"]["overall_status"] == "PASS" else 1
if __name__ == "__main__":
    raise SystemExit(main())