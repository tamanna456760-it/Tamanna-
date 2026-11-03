#!/usr/bin/env python3
"""Run repository-wide Python, Bash, JSON, and YAML syntax checks."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache"}
failures: list[str] = []

def candidates(suffixes: set[str]):
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        yield path

with tempfile.TemporaryDirectory(prefix="tamanna-pycache-") as cache_dir:
    env = os.environ.copy()
    env["PYTHONPYCACHEPREFIX"] = cache_dir
    py_files = sorted(candidates({".py"}))
    for path in py_files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        if result.returncode:
            failures.append(f"PY {path.relative_to(ROOT)}: {(result.stderr or result.stdout).strip()}")

sh_files = sorted(candidates({".sh"}))
for path in sh_files:
    result = subprocess.run(
        ["bash", "-n", str(path)], cwd=ROOT, capture_output=True, text=True,
    )
    if result.returncode:
        failures.append(f"SH {path.relative_to(ROOT)}: {(result.stderr or result.stdout).strip()}")

json_files = sorted(candidates({".json"}))
for path in json_files:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"JSON {path.relative_to(ROOT)}: {exc}")

try:
    import yaml
except ImportError as exc:
    failures.append(f"YAML parser unavailable: {exc}")
    yaml = None

yaml_files = sorted(candidates({".yaml", ".yml"}))
if yaml is not None:
    for path in yaml_files:
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"YAML {path.relative_to(ROOT)}: {exc}")

print(f"Python files checked: {len(py_files)}")
print(f"Shell files checked: {len(sh_files)}")
print(f"JSON files checked: {len(json_files)}")
print(f"YAML files checked: {len(yaml_files)}")
if failures:
    print(f"FAILURES: {len(failures)}")
    print("\n".join(failures))
    raise SystemExit(1)
print("PASS: all repository Python, Bash, JSON, and YAML syntax checks passed.")
