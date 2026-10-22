#!/usr/bin/env python3
"""Tamanna AI Endpoint Security baseline manager.
Owner: HM INSAN ALI
Creates and verifies SHA-256 baselines for explicitly selected files.
Baseline creation requires an explicit command. Existing baseline files
are never overwritten.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
DEFAULT_BASELINE = Path("data/endpoint_security_baseline.json")
MAX_FILE_SIZE = 10 * 1024 * 1024
def calculate_sha256(path: Path) -> str:
    """Calculate a SHA-256 digest for a regular, non-symlink file."""
    if path.is_symlink():
        raise ValueError("Symbolic links are not accepted.")
    if not path.is_file():
        raise ValueError("Path is not a regular file.")
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File exceeds the configured size limit.")
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()
def load_baseline(path: Path) -> dict:
    """Load and minimally validate a baseline JSON document."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Baseline root must be a JSON object.")
    if data.get("project") != PROJECT:
        raise ValueError("Baseline project does not match.")
    if not isinstance(data.get("files"), dict):
        raise ValueError("Baseline files must be a JSON object.")
    for file_path, digest in data["files"].items():
        if (
            not isinstance(file_path, str)
            or not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            raise ValueError("Baseline contains an invalid path or SHA-256.")
    return data
def create_baseline(files: list[Path], output: Path) -> dict:
    """Create a new baseline file without overwriting an existing file."""
    if output.exists() or output.is_symlink():
        raise FileExistsError("Baseline output already exists.")
    entries: dict[str, str] = {}
    for path in files:
        resolved = path.resolve(strict=True)
        digest = calculate_sha256(resolved)
        entries[str(resolved)] = digest
    baseline = {
        "project": PROJECT,
        "owner": OWNER,
        "algorithm": "sha256",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": entries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental replacement of an existing file.
    with output.open("x", encoding="utf-8") as file:
        json.dump(baseline, file, indent=2, ensure_ascii=False)
        file.write("\n")
    return baseline
def verify_baseline(baseline_path: Path) -> tuple[int, list[str]]:
    """Verify stored hashes and return (checked_count, changed_paths)."""
    baseline = load_baseline(baseline_path)
    checked = 0
    problems: list[str] = []
    for stored_path, expected_hash in baseline["files"].items():
        path = Path(stored_path)
        try:
            actual_hash = calculate_sha256(path)
        except (OSError, ValueError):
            problems.append(f"{stored_path}: missing, inaccessible, or invalid")
            continue
        checked += 1
        if actual_hash != expected_hash:
            problems.append(f"{stored_path}: hash mismatch")
    return checked, problems
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage Tamanna AI SHA-256 file baselines."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("files", nargs="+", type=Path)
    create_parser.add_argument("--output", type=Path, default=DEFAULT_BASELINE)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument(
        "--baseline", type=Path, default=DEFAULT_BASELINE
    )
    args = parser.parse_args()
    try:
        if args.command == "create":
            print(
                "WARNING: Confirm these files are trusted before creating "
                "a baseline."
            )
            baseline = create_baseline(args.files, args.output)
            print(f"Baseline created for {len(baseline['files'])} file(s).")
            print(f"Saved to: {args.output}")
            return 0
        checked, problems = verify_baseline(args.baseline)
        print(f"Files verified: {checked}")
        print(f"Problems found: {len(problems)}")
        for problem in problems:
            print(f"- {problem}")
        if problems:
            return 1
        print("PASS: All baseline file hashes match.")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc.__class__.__name__}: {exc}")
        return 2
if __name__ == "__main__":
    sys.exit(main())