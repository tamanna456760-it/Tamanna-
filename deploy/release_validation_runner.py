#!/usr/bin/env python3
"""
Tamanna AI — Release Validation Runner
Owner: HM INSAN ALI
Runs existing release validation checks without modifying project files.
"""
import argparse
import subprocess
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_CHECKER = PROJECT_ROOT / "deploy" / "validate_release_manifest_schema.py"
PLACEHOLDER_CHECKER = PROJECT_ROOT / "deploy" / "release_placeholder_checker.py"
DEFAULT_MANIFEST = PROJECT_ROOT / "deploy" / "release-manifest.json"
def run_check(label: str, command: list[str]) -> bool:
    print(f"\n===== {label} =====", flush=True)
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            check=False,
        )
    except OSError as exc:
        print(f"ERROR: Could not start {label}: {exc}", file=sys.stderr)
        return False
    if result.returncode != 0:
        print(f"FAIL: {label} (exit code {result.returncode})")
        return False
    print(f"PASS: {label}")
    return True
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Tamanna AI release-manifest validation checks."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the release manifest JSON.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=PROJECT_ROOT / "deploy" / "release_manifest.schema.json",
        help="Path to the release JSON Schema.",
    )
    args = parser.parse_args()
    manifest = args.input
    schema = args.schema
    if not manifest.is_absolute():
        manifest = PROJECT_ROOT / manifest
    if not schema.is_absolute():
        schema = PROJECT_ROOT / schema
    checks = [
        (
            "JSON Schema validation",
            [
                sys.executable,
                str(SCHEMA_CHECKER),
                "--schema",
                str(schema),
                "--input",
                str(manifest),
            ],
        ),
        (
            "Placeholder and format check",
            [
                sys.executable,
                str(PLACEHOLDER_CHECKER),
                "--input",
                str(manifest),
            ],
        ),
    ]
    results = []
    for label, command in checks:
        results.append(run_check(label, command))
    passed = sum(results)
    total = len(results)
    print(f"\n===== SUMMARY: {passed}/{total} checks passed =====")
    if passed != total:
        print("FAIL: Do not treat this manifest as release-ready.")
        return 1
    print("PASS: All configured local validation checks passed.")
    print("This does not verify scan authenticity, approval, or image provenance.")
    return 0
if __name__ == "__main__":
    sys.exit(main())