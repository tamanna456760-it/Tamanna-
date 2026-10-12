"""Tamanna AI Firewall diagnostic command-line interface.
Owner: HM INSAN ALI
This CLI performs read-only diagnostics.
It does not change operating-system firewall rules.
"""
import argparse
import json
import sys
from firewall.doctor import run_diagnostics
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Tamanna AI Firewall diagnostics."
    )
    parser.add_argument(
        "--base-dir",
        default=None,
        help="Project directory to inspect.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero exit code if issues are found.",
    )
    args = parser.parse_args()
    try:
        report = run_diagnostics(base_dir=args.base_dir)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        status = report.get("status", "ISSUES_FOUND")
        if args.strict and status != "OK":
            return 1
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(
            json.dumps(
                {
                    "project": "Tamanna AI",
                    "owner": "HM INSAN ALI",
                    "status": "ERROR",
                    "error": str(exc),
                    "system_firewall_modified": False,
                },
                indent=2,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2
if __name__ == "__main__":
    raise SystemExit(main())