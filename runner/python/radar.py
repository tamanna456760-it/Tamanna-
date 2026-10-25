#!/usr/bin/env python3
"""
Tamanna AI - Radar Scanner
Owner: HM INSAN ALI
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
}

SUSPICIOUS_EXTENSIONS = {
    ".exe", ".dll", ".bat", ".cmd", ".ps1", ".scr"
}

MAX_FILE_SIZE = 5 * 1024 * 1024


def calculate_sha256(file_path):
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def scan_file(file_path, root):
    result = {
        "path": str(file_path.relative_to(root)),
        "status": "ok",
        "findings": [],
    }

    try:
        if file_path.is_symlink() or not file_path.is_file():
            result["status"] = "skipped"
            return result

        size = file_path.stat().st_size
        result["size_bytes"] = size

        if size > MAX_FILE_SIZE:
            result["status"] = "skipped_too_large"
            return result

        result["sha256"] = calculate_sha256(file_path)

        if file_path.suffix.lower() in SUSPICIOUS_EXTENSIONS:
            result["findings"].append({
                "type": "suspicious_extension",
                "severity": "review",
            })

        if file_path.suffix.lower() in {".py", ".js", ".sh"}:
            content = file_path.read_text(
                encoding="utf-8",
                errors="replace",
            )

            patterns = (
                "eval(",
                "exec(",
                "shell=True",
                "os.system(",
            )

            for line_number, line in enumerate(
                content.splitlines(), start=1
            ):
                for pattern in patterns:
                    if pattern in line:
                        result["findings"].append({
                            "type": "code_pattern",
                            "pattern": pattern,
                            "line": line_number,
                            "severity": "review",
                        })

    except OSError as error:
        result["status"] = "error"
        result["error"] = str(error)

    return result


def scan_directory(directory="."):
    root = Path(directory).resolve()

    if not root.is_dir():
        raise NotADirectoryError(str(root))

    results = []

    for current in root.rglob("*"):
        if any(part in SKIP_DIRS for part in current.parts):
            continue

        if current.is_file() or current.is_symlink():
            results.append(scan_file(current, root))

    return {
        "scanner": "Tamanna Radar",
        "owner": "HM INSAN ALI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "directory": str(root),
        "files_scanned": len(results),
        "findings_count": sum(
            len(item["findings"]) for item in results
        ),
        "results": results,
        "read_only": True,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Tamanna AI read-only Radar scanner"
    )
    parser.add_argument("directory", nargs="?", default=".")
    parser.add_argument(
        "--output",
        default="tamanna_radar_report.json",
    )
    args = parser.parse_args()

    report = scan_directory(args.directory)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Tamanna Radar scan complete")
    print(f"Files scanned: {report['files_scanned']}")
    print(f"Findings: {report['findings_count']}")
    print(f"Report: {output}")
    print("Source files were not modified.")


if __name__ == "__main__":
    main()