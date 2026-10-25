
#!/usr/bin/env python3
"""
Tamanna AI — Safe Repository Code Scanner
Owner: HM INSAN ALI

Scans supported source/config files without modifying them.
Creates report.txt for the GitHub Actions workflow.
"""

from __future__ import annotations

import ast
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report.txt"

SCAN_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yml", ".yaml"}
EXCLUDED_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "env", "dist", "build", ".next", "coverage",
}
EXCLUDED_FILES = {
    ".env", ".env.local", ".env.production",
    "credentials.json", "token.txt",
}
MAX_FILE_BYTES = 1_000_000

findings: list[str] = []
scanned = 0
skipped = 0


def add(level: str, path: Path, message: str, line: int | None = None) -> None:
    relative = path.relative_to(ROOT).as_posix()
    location = f":{line}" if line is not None else ""
    findings.append(f"[{level}] {relative}{location} - {message}")


def scan_file(path: Path) -> None:
    global scanned, skipped

    if path.name in EXCLUDED_FILES or path.is_symlink():
        skipped += 1
        return

    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            add("SKIP", path, "File exceeds 1 MB scan limit")
            skipped += 1
            return

        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        add("WARN", path, f"Could not read file ({type(exc).__name__})")
        skipped += 1
        return

    scanned += 1
    suffix = path.suffix.lower()

    if suffix == ".py":
        try:
            ast.parse(content, filename=str(path))
        except SyntaxError as exc:
            add("ERROR", path, "Python syntax error", exc.lineno)

    elif suffix == ".json":
        try:
            json.loads(content)
        except json.JSONDecodeError as exc:
            add("ERROR", path, "Invalid JSON", exc.lineno)

    for number, line in enumerate(content.splitlines(), start=1):
        if line.rstrip() != line:
            add("STYLE", path, "Trailing whitespace", number)

        if "TODO" in line or "FIXME" in line:
            add("INFO", path, "TODO/FIXME marker found", number)

        # Report only the presence of a possible secret pattern.
        # Never print the matched value.
        upper = line.upper()
        secret_markers = (
            "OPENAI_API_KEY", "GEMINI_API_KEY",
            "GOOGLE_API_KEY", "AWS_SECRET_ACCESS_KEY",
        )
        if any(marker in upper for marker in secret_markers):
            if "=" in line and not line.lstrip().startswith(("#", "//")):
                value = line.split("=", 1)[1].strip().strip("\"'")
                if value and not value.startswith(
                    ("${{", "${", "os.environ", "os.getenv", "process.env")
                ):
                    add("REVIEW", path, "Possible hard-coded API key/secret; inspect securely", number)


def main() -> int:
    global skipped

    print("Tamanna AI Repository Scanner")
    print(f"Repository: {ROOT}")

    for current, dirs, files in os.walk(ROOT, followlinks=False):
        dirs[:] = sorted(
            name for name in dirs
            if name not in EXCLUDED_DIRS
            and not (Path(current) / name).is_symlink()
        )

        for name in sorted(files):
            path = Path(current) / name
            if path.suffix.lower() in SCAN_EXTENSIONS:
                scan_file(path)

    errors = sum(item.startswith("[ERROR]") for item in findings)
    warnings = sum(item.startswith(("[WARN]", "[REVIEW]")) for item in findings)

    lines = [
        "TAMANNA AI — CODE SCAN REPORT",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"Repository: {ROOT.name}",
        f"Files scanned: {scanned}",
        f"Files skipped: {skipped}",
        f"Findings: {len(findings)}",
        f"Errors: {errors}",
        f"Warnings/reviews: {warnings}",
        "",
        "FINDINGS",
        "--------",
        *(findings if findings else ["No findings detected."]),
        "",
        "Note: This is a basic static scan, not a complete security audit.",
    ]

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nReport saved to: {REPORT.name}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
