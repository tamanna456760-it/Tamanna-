#!/usr/bin/env python3
"""Tamanna AI deployment preflight checks."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "index.html",
    "Main.py",
    "main.py",
    "CNAME",
    ".github/workflows/deploy.yml",
    ".github/workflows/pages.yml",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    for relative in REQUIRED_FILES:
        path = ROOT / relative

        if not path.is_file():
            fail(f"Required file missing: {relative}")

    cname = (ROOT / "CNAME").read_text(
        encoding="utf-8"
    ).strip().lower()

    if cname != "www.tamanna.com":
        fail(
            "CNAME must contain exactly "
            "www.tamanna.com"
        )

    package_json = ROOT / "package.json"

    if package_json.is_file():
        try:
            json.loads(
                package_json.read_text(
                    encoding="utf-8"
                )
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            fail(f"Invalid package.json: {exc}")

    print("PASS: Required files exist.")
    print("PASS: CNAME configuration is correct.")
    print("PASS: Deployment preflight completed.")

    print(
        "NOTE: DNS, domain ownership, "
        "GitHub Pages settings and TLS "
        "must be verified separately."
    )


if __name__ == "__main__":
    main()
