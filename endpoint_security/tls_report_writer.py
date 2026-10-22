#!/usr/bin/env python3
"""
Tamanna AI — TLS Report Writer
Owner: HM INSAN ALI
Stores a supplied TLS check result as a JSON report.
Creates a new report only; refuses to overwrite an existing file.
"""
import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
def write_tls_report(input_path, output_path):
    source = Path(input_path)
    destination = Path(output_path)
    with source.open("r", encoding="utf-8") as file:
        report = json.load(file)
    if not isinstance(report, dict):
        raise ValueError("TLS input must be a JSON object")
    if report.get("project") != PROJECT:
        raise ValueError("Unexpected project identity")
    if report.get("owner") != OWNER:
        raise ValueError("Unexpected owner identity")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Create the report atomically without overwriting an existing file.
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=".tls-report-",
        suffix=".tmp",
        dir=str(destination.parent),
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "project": PROJECT,
                    "owner": OWNER,
                    "generated_at_utc": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "read_only_source": True,
                    "source_report": report,
                },
                file,
                indent=2,
                ensure_ascii=False,
            )
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        # Atomic no-overwrite operation on the same filesystem.
        os.link(temporary_path, destination)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass
    return destination
def main():
    parser = argparse.ArgumentParser(
        description="Save a Tamanna AI TLS result as a JSON report."
    )
    parser.add_argument("--input", required=True, help="Input JSON report")
    parser.add_argument(
        "--output",
        required=True,
        help="New output JSON path; existing files are never overwritten",
    )
    args = parser.parse_args()
    try:
        output = write_tls_report(args.input, args.output)
    except FileExistsError:
        parser.error("Output already exists; choose a new filename")
    except (OSError, json.JSONDecodeError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print(f"TLS report saved: {output}")
if __name__ == "__main__":
    main()