#!/usr/bin/env python3
"""
Tamanna AI — Release Manifest Schema Validator
Owner: HM INSAN ALI
Validates a release manifest against the project's JSON Schema.
Read-only: does not deploy, modify, or overwrite project files.
"""
import argparse
import json
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = PROJECT_ROOT / "deploy" / "release_manifest.schema.json"
DEFAULT_MANIFEST = PROJECT_ROOT / "deploy" / "release-manifest.json"
def load_json(path: Path):
    """Load a JSON file and report readable errors."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {path}, line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        )
    except OSError as exc:
        raise ValueError(f"Cannot read {path}: {exc}")
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Tamanna AI release manifest using JSON Schema."
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Path to the release JSON Schema.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the release manifest JSON.",
    )
    args = parser.parse_args()
    try:
        schema = load_json(args.schema)
        manifest = load_json(args.input)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
    except ImportError:
        print(
            "FAIL: Missing dependency 'jsonschema'. Install it with:\n"
            "python3 -m pip install 'jsonschema>=4.20,<5.0'",
            file=sys.stderr,
        )
        return 2
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        errors = sorted(
            validator.iter_errors(manifest),
            key=lambda error: (
                tuple(str(part) for part in error.absolute_path),
                error.message,
            ),
        )
    except SchemaError as exc:
        print(f"FAIL: Invalid JSON Schema: {exc.message}", file=sys.stderr)
        return 2
    if errors:
        print("FAIL: Release manifest does not match the schema.")
        for error in errors:
            location = ".".join(str(part) for part in error.absolute_path)
            location = location or "<root>"
            print(f"- {location}: {error.message}")
        return 1
    print("PASS: Release manifest matches the JSON Schema.")
    print(f"Project: {manifest['project']}")
    print(f"Owner: {manifest['owner']}")
    print(f"Release ID: {manifest['release_id']}")
    print("Note: Schema validation does not prove approval authenticity,")
    print("image provenance, or that a security scan really occurred.")
    return 0
if __name__ == "__main__":
    sys.exit(main())