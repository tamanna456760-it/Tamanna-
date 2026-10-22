#!/usr/bin/env python3
"""Offline dependency declaration checker for Tamanna AI.
Owner: HM INSAN ALI
This tool checks dependency declarations only.
It does not download, install, upgrade, or remove packages.
It does not verify published vulnerability databases.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
DEFAULT_REQUIREMENTS = Path("endpoint_security/requirements.txt")
# Accepts common exact pins, e.g. package==1.2.3 or package[extra]==1.2.3.
EXACT_PIN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*(?:\[[A-Za-z0-9_,.-]+\])?=="
    r"[A-Za-z0-9][A-Za-z0-9.!+_-]*$"
)
def check_requirements(path: Path) -> dict[str, Any]:
    checked = 0
    pinned: list[str] = []
    unpinned: list[dict[str, Any]] = []
    ignored: list[int] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            # Editable, URL, and nested requirements need separate review.
            if (
                line.startswith(("-e ", "--editable ", "-r ", "--requirement "))
                or "://" in line
                or line.startswith((".", "/"))
            ):
                ignored.append(line_number)
                continue
            checked += 1
            if EXACT_PIN.fullmatch(line):
                pinned.append(line.split("==", 1)[0])
            else:
                unpinned.append({
                    "line": line_number,
                    "requirement": line,
                    "reason": "No exact == version pin detected",
                })
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "component": "Endpoint Security",
        "report_type": "offline_dependency_declaration_check",
        "requirements_file": path.name,
        "checked_entries": checked,
        "exactly_pinned_count": len(pinned),
        "unpinned_count": len(unpinned),
        "pinned_packages": pinned,
        "unpinned_entries": unpinned,
        "ignored_line_numbers": ignored,
        "limitations": [
            "This is not a vulnerability scan.",
            "Version pinning does not prove a package is safe.",
            "Ignored lines require manual review.",
            "No network requests or package installations are performed.",
        ],
        "status": "PASS" if not unpinned else "REVIEW_REQUIRED",
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check dependency version declarations offline."
    )
    parser.add_argument(
        "--requirements",
        type=Path,
        default=DEFAULT_REQUIREMENTS,
        help="Path to a requirements.txt file.",
    )
    args = parser.parse_args()
    try:
        report = check_requirements(args.requirements)
    except OSError as exc:
        print(f"ERROR: Cannot read requirements file ({exc.__class__.__name__}).")
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1
if __name__ == "__main__":
    sys.exit(main())