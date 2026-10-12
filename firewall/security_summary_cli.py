"""
Tamanna AI Firewall - Security Summary CLI
Owner: HM INSAN ALI
Command-line interface for viewing security summaries.
"""
import argparse
import json
import sys
from pathlib import Path
from firewall.security_summary import (
    build_security_summary,
    save_security_summary,
)
def build_parser() -> argparse.ArgumentParser:
    base_dir = Path(__file__).parent
    parser = argparse.ArgumentParser(
        description="Tamanna AI Firewall Security Summary",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=base_dir / "reports" / "event_report.json",
        help="Path to the existing event report JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save the summary JSON.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if the report is invalid or high-risk events exist.",
    )
    return parser
def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.output is not None:
        summary = save_security_summary(
            report_path=args.report,
            output_path=args.output,
        )
        if summary.get("save_error"):
            print(
                f"Error saving summary: {summary['save_error']}",
                file=sys.stderr,
            )
            return 2
    else:
        summary = build_security_summary(args.report)
    print(json.dumps(summary, indent=2))
    if not summary["report_valid"]:
        return 1 if args.strict else 0
    if (
        args.strict
        and summary.get("high_risk_events", 0) > 0
    ):
        return 1
    return 0
if __name__ == "__main__":
    raise SystemExit(main())