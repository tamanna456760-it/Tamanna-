#!/usr/bin/env python3
"""
Tamanna AI — Release Validation Report Writer
Owner: HM INSAN ALI
Converts supplied validation results into a new JSON report.
Never overwrites an existing report.
"""
import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
PROJECT_NAME = "Tamanna AI"
OWNER = "HM INSAN ALI"
def load_results(path: Path):
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise ValueError(f"Results file not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        )
    if not isinstance(data, dict):
        raise ValueError("Results JSON must be an object.")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("'checks' must be a non-empty list.")
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise ValueError(f"checks[{index}] must be an object.")
        if not isinstance(check.get("name"), str) or not check["name"].strip():
            raise ValueError(f"checks[{index}].name must be a non-empty string.")
        if check.get("status") not in ("PASS", "FAIL", "SKIP"):
            raise ValueError(
                f"checks[{index}].status must be PASS, FAIL, or SKIP."
            )
    return data
def write_new_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents overwriting an existing report.
    with path.open("x", encoding="utf-8") as file:
        file.write(content)
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a Tamanna AI release-validation report."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        results = load_results(args.input)
    except (ValueError, OSError) as exc:
        print(f"FAIL: {exc}")
        return 2
    checks = results["checks"]
    passed = sum(item["status"] == "PASS" for item in checks)
    failed = sum(item["status"] == "FAIL" for item in checks)
    skipped = sum(item["status"] == "SKIP" for item in checks)
    report = {
        "project": PROJECT_NAME,
        "owner": OWNER,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_status": (
            "PASS" if failed == 0 and skipped == 0 and passed == len(checks)
            else "FAIL"
        ),
        "summary": {
            "total": len(checks),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "checks": checks,
        "limitations": [
            "This report reflects supplied results only.",
            "It does not independently execute or verify security scans.",
            "It does not prove release approval or image provenance.",
        ],
    }
    output = args.output
    if not output.is_absolute():
        output = Path.cwd() / output
    try:
        write_new_file(
            output,
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        )
    except FileExistsError:
        print(f"FAIL: Refusing to overwrite existing report: {output}")
        return 1
    except OSError as exc:
        print(f"FAIL: Cannot write report: {exc}")
        return 2
    print(f"Report created: {output}")
    print(f"Overall status: {report['overall_status']}")
    print(f"PASS={passed}, FAIL={failed}, SKIP={skipped}")
    return 0 if report["overall_status"] == "PASS" else 1
if __name__ == "__main__":
    raise SystemExit(main())