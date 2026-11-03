#!/usr/bin/env python3
"""Stable root entry point for the Tamanna repository scanner."""
from pathlib import Path
import runpy
import sys

REPO_ROOT = Path(__file__).resolve().parent
SCANNER = REPO_ROOT / "runner" / "python" / "tamanna_head.py"

if not SCANNER.is_file():
    print(f"ERROR: Tamanna scanner file is missing: {SCANNER}", file=sys.stderr)
    raise SystemExit(2)

# Use the repository root as the scanner's working directory.
import os
os.chdir(REPO_ROOT)
runpy.run_path(str(SCANNER), run_name="__main__")
