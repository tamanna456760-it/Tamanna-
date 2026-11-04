"""Command line entry point: python -m data.training_pipeline.cli SOURCE OUTPUT."""

from __future__ import annotations

import argparse
import json

from .pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare local Tamanna AI text, code, conversation and media datasets.")
    parser.add_argument("source", help="Local source file or directory")
    parser.add_argument("output", help="Output directory (must be outside source)")
    parser.add_argument("--min-chars", type=int, default=20)\n    parser.add_argument("--provenance", help="JSON manifest; when supplied, only explicitly approved files are ingested")
    args = parser.parse_args()
    if args.min_chars < 1:
        parser.error("--min-chars must be at least 1")
    print(json.dumps(run_pipeline(args.source, args.output, min_chars=args.min_chars, provenance_path=args.provenance), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
