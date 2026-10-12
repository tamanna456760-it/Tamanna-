"""
Tamanna AI Firewall - Security Status CLI
Owner: HM INSAN ALI
"""
import argparse
import json
import sys
from pathlib import Path
from firewall.security_status import (
    check_security_status,
    save_security_status,
)
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Tamanna AI Firewall Security Status",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).parent,
        help="Firewall directory containing firewall_config.json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save the status JSON.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if required files or config are invalid.",
    )
    args = parser.parse_args(argv)
    if args.output:
        result = save_security_status(
            output_path=args.output,
            base_dir=args.base_dir,
        )
        if result.get("save_error"):
            print(
                f"Unable to save status: {result['save_error']}",
                file=sys.stderr,
            )
            return 2
    else:
        result = check_security_status(args.base_dir)
    print(json.dumps(result, indent=2))
    if args.strict and result["status"] != "READY_FOR_REVIEW":
        return 1
    return 0
if __name__ == "__main__":
    raise SystemExit(main())