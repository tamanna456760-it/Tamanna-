
#!/usr/bin/env python3
"""
Tamanna AI - Safe Fix Planner
Owner: HM INSAN ALI

Reads analyzer findings and creates a proposed-fixes report.
Does not modify source files or execute project code.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_REPORT = (
    Path(os.environ.get("RUNNER_TEMP", "/tmp"))
    / "tamanna_analyzer_report.json"
)

OUTPUT_REPORT = Path(
    os.environ.get(
        "TAMANNA_FIXER_REPORT",
        str(
            Path(os.environ.get("RUNNER_TEMP", "/tmp"))
            / "tamanna_fix_plan.json"
        ),
    )
)


def load_findings(report_path: Path) -> dict:
    """Load and validate the analyzer JSON report."""
    if not report_path.is_file():
        raise FileNotFoundError(
            f"Analyzer report not found: {report_path}"
        )

    with report_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Analyzer report must be a JSON object.")

    findings = data.get("findings", [])

    if not isinstance(findings, list):
        raise ValueError("'findings' must be a JSON list.")

    return data


def create_fix_plan(report: dict) -> dict:
    """Create a review-only plan; never edit source files."""
    findings = report.get("findings", [])
    planned = []

    for item in findings:
        if not isinstance(item, dict):
            continue

        severity = str(item.get("severity", "review")).lower()
        message = str(
            item.get("message", item.get("rule", "Review finding"))
        )
        file_path = str(item.get("file", item.get("path", "")))

        # Do not suggest automatic edits to secrets or credentials.
        sensitive = any(
            word in (message + " " + file_path).lower()
            for word in (
                "secret",
                "token",
                "credential",
                "private key",
                "api key",
                "password",
            )
        )

        if sensitive:
            action = (
                "MANUAL_REVIEW: verify exposure; rotate any exposed "
                "credential and move secrets to GitHub Actions Secrets."
            )
        elif "syntax" in message.lower():
            action = (
                "REVIEW: inspect the reported Python syntax error, "
                "then run py_compile after a manual correction."
            )
        elif "json" in message.lower():
            action = (
                "REVIEW: validate the JSON file and correct its syntax."
            )
        elif "eval" in message.lower() or "exec" in message.lower():
            action = (
                "REVIEW: inspect dynamic execution and replace it "
                "with a safer, narrowly scoped alternative if possible."
            )
        else:
            action = (
                "MANUAL_REVIEW: inspect the finding and add a tested "
                "fix before changing the source file."
            )

        planned.append(
            {
                "file": file_path,
                "severity": severity,
                "finding": message,
                "proposed_action": action,
                "automatic_edit": False,
            }
        )

    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "review-only",
        "source_files_modified": False,
        "finding_count": len(planned),
        "fixes": planned,
    }


def main() -> int:
    report_path = Path(
        os.environ.get(
            "TAMANNA_ANALYZER_REPORT",
            str(DEFAULT_REPORT),
        )
    )

    try:
        report = load_findings(report_path)
        plan = create_fix_plan(report)

        OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_REPORT.open("w", encoding="utf-8") as file:
            json.dump(plan, file, indent=2, ensure_ascii=False)
            file.write("\n")

        print(f"Tamanna Fix Planner: {plan['finding_count']} finding(s)")
        print(f"Source files modified: {plan['source_files_modified']}")
        print(f"Plan saved to: {OUTPUT_REPORT}")
        return 0

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
