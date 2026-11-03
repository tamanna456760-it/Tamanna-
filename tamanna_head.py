#!/usr/bin/env python3
"""Root compatibility entry point for the Tamanna HEAD scanner."""
from pathlib import Path
import runpy

script = Path(__file__).resolve().parent / "runner" / "python" / "tamanna_head.py"
if not script.is_file():
    raise SystemExit(f"Tamanna HEAD scanner not found: {script}")
runpy.run_path(str(script), run_name="__main__")
