#!/usr/bin/env python3
"""
Tamanna AI — Environment Preflight Checker
Owner: HM INSAN ALI
Checks required environment variable names without printing values.
Read-only: does not change environment or deployment settings.
"""
import argparse
import json
import os
from pathlib import Path
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
# Add a variable here only if the application genuinely requires it.
DEFAULT_REQUIRED = ("TAMANNA_ENV",)
def check_environment(required_names, env_file=None):
    findings = []
    checks = []
    env_names = set(os.environ)
    # Parse variable names only; never print values.
    if env_file:
        path = Path(env_file)
        if not path.is_file():
            findings.append("Environment file is missing.")
        else:
            try:
                for line in path.read_text(
                    encoding="utf-8"
                ).splitlines():
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    if "=" not in stripped:
                        continue
                    key = stripped.split("=", 1)[0].strip()
                    if key and key.replace("_", "").isalnum():
                        env_names.add(key)
            except (OSError, UnicodeError):
                findings.append("Environment file could not be read.")
    for name in required_names:
        present = name in env_names
        checks.append({
            "name": name,
            "present": present,
        })
        if not present:
            findings.append(
                f"Required environment variable is missing: {name}"
            )
    return {
        "project": PROJECT,
        "owner": OWNER,
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "checks": checks,
        "findings": findings,
        "read_only": True,
        "note": (
            "Checks variable names only. Does not validate secret values, "
            "permissions, or whether the application can use them."
        ),
    }
def main():
    parser = argparse.ArgumentParser(
        description="Check Tamanna AI deployment environment variables."
    )
    parser.add_argument(
        "--env-file",
        help="Optional path to an environment file; values are not printed",
    )
    parser.add_argument(
        "--required",
        nargs="*",
        default=list(DEFAULT_REQUIRED),
        help="Required variable names (default: TAMANNA_ENV)",
    )
    args = parser.parse_args()
    report = check_environment(args.required, args.env_file)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
if __name__ == "__main__":
    main()