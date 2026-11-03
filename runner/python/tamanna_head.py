#!/usr/bin/env python3
"""Build a JSON manifest of repository files without modifying source files."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "tamanna_meta"
OUTPUT_FILE = OUTPUT_DIR / "manifest.json"

IGNORE_DIRS = {
    ".git", ".github", ".venv", "venv", "__pycache__", "node_modules",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "tamanna_meta",
}
IGNORE_FILES = {".env", ".ven", "id_rsa", "id_ed25519"}
MAX_FILES = 100000


def scan_repo(root: Path = REPO_ROOT) -> list[Path]:
    found: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORE_DIRS)
        for filename in sorted(files):
            if filename in IGNORE_FILES or filename.endswith((".pyc", ".pyo")):
                continue
            path = Path(current) / filename
            try:
                relative = path.relative_to(root)
            except ValueError:
                continue
            found.append(relative)
            if len(found) >= MAX_FILES:
                return found
    return found


def build_manifest(files: list[Path]) -> dict:
    entries = []
    for relative in files:
        absolute = REPO_ROOT / relative
        try:
            size = absolute.stat().st_size
        except OSError:
            size = None
        entries.append({"path": relative.as_posix(), "size": size})

    return {
        "tamanna_head": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_files": len(entries),
        "files": entries,
    }


def main() -> int:
    files = scan_repo()
    manifest = build_manifest(files)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT_FILE.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(OUTPUT_FILE)
    print(f"PASS: Tamanna HEAD manifest created: {OUTPUT_FILE.relative_to(REPO_ROOT)}")
    print(f"PASS: indexed {manifest['total_files']} repository files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
