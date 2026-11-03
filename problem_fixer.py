#!/usr/bin/env python3
"""Backward-compatible entry point for the safe Tamanna fix planner.

Older automation may still invoke python problem_fixer.py.
The maintained implementation lives in scripts/fixer.py and only
writes a review plan; it never edits project source files.
"""
from pathlib import Path
import os
import runpy
import sys

ROOT = Path(__file__).resolve().parent
REPORT = Path(
    os.environ.get(
        "TAMANNA_ANALYZER_REPORT",
        str(Path(os.getenv("RUNNER_TEMP", "/tmp")) / "tamanna_analyzer_report.json"),
    )
)
FIXER = ROOT / "scripts" / "fixer.py"

if not REPORT.is_file():
    print(f"SKIP: analyzer report not found at {REPORT}; no source files changed.")
    raise SystemExit(0)

if not FIXER.is_file():
    print(f"ERROR: safe fix planner not found: {FIXER}", file=sys.stderr)
    raise SystemExit(2)

runpy.run_path(str(FIXER), run_name="__main__")
