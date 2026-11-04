"""CLI for preparing SFT and human-preference datasets."""

from __future__ import annotations

import argparse
import json

from .preferences import export_preference_dataset
from .sft import export_sft_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare Tamanna AI learning datasets; no model training is started.")
    sub = parser.add_subparsers(dest="command", required=True)
    sft = sub.add_parser("sft", help="Prepare supervised fine-tuning examples")
    sft.add_argument("source")
    sft.add_argument("output")
    prefs = sub.add_parser("preferences", help="Prepare human-reviewed preference pairs")
    prefs.add_argument("source")
    prefs.add_argument("output")
    args = parser.parse_args()
    if args.command == "sft":
        result = export_sft_dataset(args.source, args.output)
    else:
        result = export_preference_dataset(args.source, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
