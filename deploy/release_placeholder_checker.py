#!/usr/bin/env python3
"""
Tamanna AI — Release Placeholder Checker
Owner: HM INSAN ALI
Checks a release manifest for common example or placeholder values.
Read-only. This does not verify approval authenticity, scan results,
image provenance, or deployment readiness.
"""
import argparse
import json
import re
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = PROJECT_ROOT / "deploy" / "release-manifest.json"
PLACEHOLDER_TEXT = (
    "example",
    "placeholder",
    "replace_with",
    "replace-me",
    "your-value",
    "your_value",
    "todo",
)
SHA256_PATTERN = re.compile(r"^.+@sha256:([0-9a-fA-F]{64})$")
def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError(f"Manifest not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        )
    except OSError as exc:
        raise ValueError(f"Cannot read manifest: {exc}")
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find common placeholder values in a Tamanna AI manifest."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the release manifest JSON.",
    )
    args = parser.parse_args()
    try:
        manifest = load_json(args.input)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    if not isinstance(manifest, dict):
        print("FAIL: Manifest root must be a JSON object.", file=sys.stderr)
        return 2
    findings = []
    def inspect(value, path="$"):
        if isinstance(value, dict):
            for key, child in value.items():
                inspect(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                inspect(child, f"{path}[{index}]")
        elif isinstance(value, str):
            lowered = value.lower()
            if any(marker in lowered for marker in PLACEHOLDER_TEXT):
                findings.append(
                    f"{path}: contains a possible placeholder value"
                )
    inspect(manifest)
    images = manifest.get("images")
    if not isinstance(images, dict) or not images:
        findings.append("$.images: must contain at least one image reference")
    else:
        for name, reference in images.items():
            if not isinstance(reference, str):
                findings.append(f"$.images.{name}: reference must be a string")
                continue
            match = SHA256_PATTERN.fullmatch(reference)
            if not match:
                findings.append(
                    f"$.images.{name}: expected an immutable "
                    "image reference ending in @sha256:<64 hex characters>"
                )
    commit = manifest.get("git_commit")
    if not isinstance(commit, str) or not re.fullmatch(
        r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", commit
    ):
        findings.append(
            "$.git_commit: expected a full 40- or 64-character hexadecimal hash"
        )
    if findings:
        print("FAIL: Potential release-manifest issues found.")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("PASS: No common placeholders or basic image/commit format issues found.")
    print("This result does not establish that the release is authentic or safe.")
    return 0
if __name__ == "__main__":
    sys.exit(main())