#!/usr/bin/env python3
"""Validate essential Tamanna AI release files."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    required = (
        "index.html",
        "Main.py",
        "main.py",
    )

    for relative in required:
        if not (ROOT / relative).is_file():
            fail(f"Missing release file: {relative}")

    json_files = (
        "package.json",
        "package-lock.json",
    )

    for relative in json_files:
        path = ROOT / relative

        if not path.is_file():
            continue

        try:
            json.loads(
                path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            fail(f"{relative} is invalid: {exc}")

    print("PASS: Essential release files exist.")
    print("PASS: Available JSON files are valid.")


if __name__ == "__main__":
    main()
