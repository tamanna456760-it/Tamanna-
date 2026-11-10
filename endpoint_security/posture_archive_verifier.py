#!/usr/bin/env python3
"""Read-only verification of posture archive files against a saved index."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

PROJECT_NAME = "Tamanna AI"
OWNER_NAME = "HM INSAN ALI"


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(index_path: Path, report_dir: Path) -> dict:
    if not index_path.is_file():
        raise FileNotFoundError(f"Archive index not found: {index_path}")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(index, dict):
        raise ValueError("Archive index must be a JSON object.")
    if index.get("project") != PROJECT_NAME:
        raise ValueError("Archive index project does not match Tamanna AI.")
    if index.get("owner") != OWNER_NAME:
        raise ValueError("Archive index owner does not match.")
    reports = index.get("reports")
    if not isinstance(reports, list):
        raise ValueError("Archive index must contain a reports list.")
    results: list[dict] = []
    for entry in reports:
        if not isinstance(entry, dict):
            results.append({"file": None, "status": "INVALID_INDEX_ENTRY"})
            continue
        filename = entry.get("file", entry.get("filename"))
        expected_hash = entry.get("sha256")
        if not isinstance(filename, str) or not filename or Path(filename).name != filename or filename in {".", ".."}:
            results.append({"file": filename, "status": "INVALID_FILENAME"})
            continue
        if not isinstance(expected_hash, str) or len(expected_hash) != 64 or any(char not in "0123456789abcdef" for char in expected_hash):
            results.append({"file": filename, "status": "NO_VALID_BASELINE_HASH"})
            continue
        path = report_dir / filename
        try:
            if path.is_symlink() or not path.is_file():
                results.append({"file": filename, "status": "MISSING_OR_UNSAFE_FILE"})
                continue
            actual_hash = calculate_sha256(path)
            results.append({"file": filename, "status": "MATCH" if actual_hash == expected_hash else "HASH_MISMATCH", "expected_sha256": expected_hash, "actual_sha256": actual_hash})
        except OSError:
            results.append({"file": filename, "status": "READ_ERROR"})
    statuses = [item["status"] for item in results]
    has_problem = any(status != "MATCH" for status in statuses)
    return {"project": PROJECT_NAME, "owner": OWNER_NAME, "read_only": True, "reports_checked": len(results), "reports_matching": sum(status == "MATCH" for status in statuses), "reports_with_issues": sum(status != "MATCH" for status in statuses), "status": "REVIEW_REQUIRED" if has_problem else "MATCH", "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify posture report hashes against an archive index.")
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify_archive(args.index, args.report_dir)
        rendered = json.dumps(result, indent=2, ensure_ascii=False)
        print(rendered)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as file:
                file.write(rendered + "\n")
        return 0 if result["status"] == "MATCH" else 1
    except FileExistsError:
        print("ERROR: Output already exists; choose another filename.")
        return 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
