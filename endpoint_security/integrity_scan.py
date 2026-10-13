#!/usr/bin/env python3
"""Read-only file integrity scanner for Tamanna AI.
Owner: HM INSAN ALI
Checks explicitly configured paths against an existing SHA-256 baseline.
No files are modified, deleted, quarantined, or executed.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any
from endpoint_security.baseline_manager import (
    calculate_sha256,
    load_baseline,
)
DEFAULT_CONFIG = Path("endpoint_security/endpoint_config.json")
DEFAULT_BASELINE = Path("data/endpoint_security_baseline.json")
def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        config = json.load(file)
    if not isinstance(config, dict):
        raise ValueError("Configuration root must be a JSON object.")
    integrity = config.get("file_integrity")
    if not isinstance(integrity, dict):
        raise ValueError("file_integrity configuration is missing.")
    if integrity.get("enabled") is not True:
        raise ValueError("File integrity monitoring is disabled.")
    paths = integrity.get("paths")
    if not isinstance(paths, list):
        raise ValueError("file_integrity.paths must be a list.")
    return integrity
def scan_paths(
    paths: list[str],
    baseline_path: Path,
) -> dict[str, Any]:
    baseline = load_baseline(baseline_path)
    expected = baseline["files"]
    results: list[dict[str, str]] = []
    for configured_path in paths:
        path = Path(configured_path)
        try:
            resolved = path.resolve(strict=True)
            actual_hash = calculate_sha256(resolved)
        except (OSError, ValueError):
            results.append({
                "path": configured_path,
                "status": "ERROR",
            })
            continue
        expected_hash = expected.get(str(resolved))
        if expected_hash is None:
            status = "NO_BASELINE"
        elif actual_hash == expected_hash:
            status = "MATCH"
        else:
            status = "CHANGED"
        results.append({
            "path": str(resolved),
            "status": status,
        })
    counts = {
        status: sum(1 for result in results if result["status"] == status)
        for status in ("MATCH", "CHANGED", "NO_BASELINE", "ERROR")
    }
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "component": "Endpoint Security",
        "mode": "monitor_only",
        "results": results,
        "summary": counts,
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a read-only Tamanna AI file integrity scan."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    args = parser.parse_args()
    try:
        integrity_config = load_config(args.config)
        paths = integrity_config["paths"]
        if not paths:
            print(
                "No paths configured. Add explicitly approved file paths "
                "to file_integrity.paths first."
            )
            return 1
        if not all(isinstance(path, str) and path.strip() for path in paths):
            raise ValueError("Every configured path must be a non-empty string.")
        report = scan_paths(paths, args.baseline)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        summary = report["summary"]
        if summary["CHANGED"] or summary["ERROR"]:
            return 1
        if summary["NO_BASELINE"]:
            return 1
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc.__class__.__name__}: {exc}")
        return 2
if __name__ == "__main__":
    sys.exit(main())