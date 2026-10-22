#!/usr/bin/env python3
"""Read-only readiness check for Tamanna AI Endpoint Security.
Owner: HM INSAN ALI
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FILES = [
    "endpoint_security/endpoint_config.json",
    "endpoint_security/config_validator.py",
    "endpoint_security/policy_checker.py",
    "endpoint_security/event_logger.py",
    "endpoint_security/file_integrity.py",
    "endpoint_security/baseline_manager.py",
    "endpoint_security/integrity_scan.py",
    "endpoint_security/security_audit.py",
    "endpoint_security/audit_report_verifier.py",
    "endpoint_security/audit_dashboard.py",
    "endpoint_security/tests/test_endpoint_security.py",
]
def check_readiness(root: Path) -> dict:
    results = []
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.is_file():
            status = "MISSING"
            details = "Required file was not found."
        elif path.stat().st_size == 0:
            status = "EMPTY"
            details = "File exists but has no content."
        else:
            status = "PRESENT"
            details = "File exists and is non-empty."
        results.append({
            "path": relative_path,
            "status": status,
            "details": details,
        })
    missing = sum(item["status"] == "MISSING" for item in results)
    empty = sum(item["status"] == "EMPTY" for item in results)
    present = sum(item["status"] == "PRESENT" for item in results)
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "mode": "read_only",
        "summary": {
            "total": len(results),
            "present": present,
            "missing": missing,
            "empty": empty,
            "readiness": (
                "FILES_PRESENT"
                if missing == 0 and empty == 0
                else "ACTION_REQUIRED"
            ),
        },
        "checks": results,
        "limitations": [
            "This check does not execute or validate the code.",
            "A present file is not proof that the file is safe or correct.",
            "Unit tests and the security audit must be run separately.",
        ],
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check required Tamanna AI security files."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=PROJECT_ROOT,
        help="Tamanna repository root directory.",
    )
    args = parser.parse_args()
    report = check_readiness(args.root.resolve())
    print(json.dumps(report, indent=2))
    return 0 if report["summary"]["readiness"] == "FILES_PRESENT" else 1
if __name__ == "__main__":
    raise SystemExit(main())