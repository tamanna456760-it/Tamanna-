"""Read-only local repository inventory for the legacy backup-network module.

The previous implementation embedded a GitHub personal access token and could
write restored content to the GitHub repository automatically. That behavior
has been removed. This module performs no network access and no repository
writes. Use the dedicated backup/deployment process after human review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".pytest_cache", ".mypy_cache",
}
SENSITIVE_NAMES = {
    ".env", ".env.local", ".env.production", "credentials.json",
    "secrets.json", "id_rsa", "id_ed25519",
}


def inventory(root: Path) -> dict:
    root = root.resolve()
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.name.lower() in SENSITIVE_NAMES or path.suffix.lower() in {
            ".pem", ".key", ".p12", ".pfx"
        }:
            classification = "sensitive-file-excluded"
            size = None
        else:
            classification = "file"
            try:
                size = path.stat().st_size
            except OSError:
                size = None
        files.append({
            "path": relative.as_posix(),
            "classification": classification,
            "bytes": size,
        })
    return {
        "mode": "read-only",
        "root": str(root),
        "files_scanned": len(files),
        "files": files,
        "network_access": False,
        "repository_writes": False,
        "note": "This is an inventory only, not a backup or restore operation.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f"root is not a directory: {args.root}")
    report = inventory(args.root)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output.resolve()
        if output == args.root.resolve() or args.root.resolve() not in output.parents:
            parser.error("output must be inside the selected root directory")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
