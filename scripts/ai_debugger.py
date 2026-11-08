#!/usr/bin/env python3
"""Offline, rule-based formatter for Tamanna's static scanner report.

This module deliberately performs no network requests and loads no hosted
AI SDK. It organizes scanner findings into a readable report; it is not an
LLM and does not claim to generate model-based advice.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SCAN_REPORT = ROOT / "report.txt"
OUTPUT_REPORT = ROOT / "ai_debugger_report.txt"
FINDING = re.compile(r"^\[(ERROR|WARN|REVIEW|INFO|STYLE|SKIP)\]\s+(.+)$")


def build_offline_review(report: str) -> str:
    """Group existing scanner findings without inventing new findings."""
    grouped: dict[str, list[str]] = {
        "ERROR": [],
        "WARN": [],
        "REVIEW": [],
        "INFO": [],
        "STYLE": [],
        "SKIP": [],
    }

    for line in report.splitlines():
        match = FINDING.match(line.strip())
        if match:
            grouped[match.group(1)].append(line.strip())

    lines = [
        "EXECUTIVE SUMMARY",
        "This is an offline summary of the static scanner output.",
        "No AI model or external service was used.",
        "",
        "CONFIRMED SCANNER ERRORS",
    ]

    errors = grouped["ERROR"]
    lines.extend(errors or ["No scanner errors were reported."])
    lines += ["", "SECURITY REVIEW ITEMS"]
    lines.extend(grouped["REVIEW"] or ["No review markers were reported."])
    lines += ["", "WARNINGS"]
    lines.extend(grouped["WARN"] or ["No warnings were reported."])
    lines += ["", "STYLE AND INFORMATIONAL ITEMS"]
    lines.extend(grouped["STYLE"] + grouped["INFO"] or ["No style or informational items were reported."])
    lines += ["", "SKIPPED ITEMS"]
    lines.extend(grouped["SKIP"] or ["No skipped items were reported."])
    lines += [
        "",
        "LIMITATIONS",
        "- This report only reorganizes findings already present in report.txt.",
        "- It does not execute tests, verify vulnerabilities, or modify source files.",
        "- Review each finding and run the relevant tests before merging fixes.",
        "",
        "FINDING COUNTS",
    ]
    for level, items in grouped.items():
        lines.append(f"{level}: {len(items)}")

    return "\n".join(lines) + "\n"


def main() -> int:
    if not SCAN_REPORT.is_file():
        print("ERROR: report.txt was not found. Run scripts/scan.py first.")
        return 1

    raw_report = SCAN_REPORT.read_text(encoding="utf-8")
    if not raw_report.strip():
        print("ERROR: report.txt is empty.")
        return 1

    review = build_offline_review(raw_report)
    content = (
        "TAMANNA AI — OFFLINE DIAGNOSTIC SUMMARY\n"
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}\n"
        "Mode: deterministic, rule-based; no hosted AI API\n"
        "Source: report.txt\n\n"
        f"{review}"
    )
    OUTPUT_REPORT.write_text(content, encoding="utf-8")
    print("Offline diagnostic summary generated.")
    print(f"Report saved: {OUTPUT_REPORT.name}")
    print("No network requests were made and no source files were modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
