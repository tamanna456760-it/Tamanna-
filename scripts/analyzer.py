
#!/usr/bin/env python3
"""
Tamanna AI - Safe Code Analyzer
Owner: HM INSAN ALI

Features:
- Python syntax analysis
- JSON validation
- Basic security pattern detection
- JSON report generation
- Read-only source scanning

This analyzer never modifies source files.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}

SCAN_EXTENSIONS = {".py", ".json"}

SECRET_PATTERNS = [
    (
        "HIGH",
        "Possible private key",
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
        ),
    ),
    (
        "HIGH",
        "Possible Google API key",
        re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    ),
    (
        "MEDIUM",
        "Possible hardcoded API key or secret",
        re.compile(
            r"""(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token)"""
            r"""\b\s*[:=]\s*['"][^'"\s]{12,}['"]"""
        ),
    ),
]

PLACEHOLDER_VALUES = {
    "your_api_key",
    "your-api-key",
    "replace_me",
    "changeme",
    "example",
    "placeholder",
}


def relative_path(path: Path) -> str:
    """Return a project-relative path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def add_finding(
    findings: list[dict[str, Any]],
    path: Path,
    severity: str,
    category: str,
    message: str,
    line: int | None = None,
) -> None:
    """Add a structured finding to the report."""
    findings.append(
        {
            "file": relative_path(path),
            "line": line,
            "severity": severity,
            "category": category,
            "message": message,
        }
    )


def should_skip(path: Path) -> bool:
    """Skip generated, dependency, and hidden Git directories."""
    try:
        parts = path.relative_to(PROJECT_ROOT).parts
    except ValueError:
        return True

    return any(part in SKIP_DIRS for part in parts)


def analyze_python(
    path: Path,
    findings: list[dict[str, Any]],
) -> None:
    """Parse Python source and inspect basic risky patterns."""
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        add_finding(
            findings, path, "MEDIUM", "READ_ERROR", str(exc)
        )
        return

    try:
        ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        add_finding(
            findings,
            path,
            "HIGH",
            "PYTHON_SYNTAX",
            exc.msg,
            exc.lineno,
        )

    for line_number, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()

        # Skip empty lines and ordinary comments.
        if not stripped or stripped.startswith("#"):
            continue

        if re.search(r"\beval\s*\(", line):
            add_finding(
                findings,
                path,
                "MEDIUM",
                "DYNAMIC_EXECUTION",
                "Review eval(); untrusted input must never be evaluated.",
                line_number,
            )

        if re.search(r"\bexec\s*\(", line):
            add_finding(
                findings,
                path,
                "MEDIUM",
                "DYNAMIC_EXECUTION",
                "Review exec(); dynamic code execution is risky.",
                line_number,
            )

        for severity, message, pattern in SECRET_PATTERNS:
            match = pattern.search(line)
            if not match:
                continue

            # Ignore obvious placeholder values to reduce false alarms.
            matched_text = match.group(0).lower()
            if any(value in matched_text for value in PLACEHOLDER_VALUES):
                continue

            add_finding(
                findings,
                path,
                severity,
                "POSSIBLE_SECRET",
                message,
                line_number,
            )


def analyze_json(
    path: Path,
    findings: list[dict[str, Any]],
) -> None:
    """Validate JSON syntax without changing the file."""
    try:
        with path.open("r", encoding="utf-8") as file:
            json.load(file)
    except json.JSONDecodeError as exc:
        add_finding(
            findings,
            path,
            "HIGH",
            "JSON_SYNTAX",
            f"{exc.msg} (line {exc.lineno}, column {exc.colno})",
            exc.lineno,
        )
    except (OSError, UnicodeError) as exc:
        add_finding(
            findings, path, "MEDIUM", "READ_ERROR", str(exc)
        )


def discover_files() -> list[Path]:
    """Find supported source files in the project."""
    files: list[Path] = []

    for current, directories, filenames in os.walk(PROJECT_ROOT):
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in SKIP_DIRS
            and not directory.startswith(".git")
        )

        current_path = Path(current)

        for filename in filenames:
            path = current_path / filename

            if path.suffix.lower() not in SCAN_EXTENSIONS:
                continue

            if should_skip(path):
                continue

            files.append(path)

    return sorted(files)


def main() -> int:
    findings: list[dict[str, Any]] = []
    files = discover_files()

    print("=" * 58)
    print(" TAMANNA AI - SAFE CODE ANALYZER")
    print(" Owner: HM INSAN ALI")
    print("=" * 58)
    print(f"Project: {PROJECT_ROOT}")
    print(f"Files discovered: {len(files)}")
    print()

    for path in files:
        if path.suffix.lower() == ".py":
            analyze_python(path, findings)
        elif path.suffix.lower() == ".json":
            analyze_json(path, findings)

    report = {
        "tool": "Tamanna AI Safe Code Analyzer",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": str(PROJECT_ROOT),
        "files_scanned": len(files),
        "findings_count": len(findings),
        "findings": findings,
    }

    # Store reports outside the repository to avoid modifying project files.
    report_path = Path(
        os.environ.get(
            "TAMANNA_ANALYZER_REPORT",
            str(Path(os.getenv("RUNNER_TEMP", "/tmp"))
                / "tamanna_analyzer_report.json"),
        )
    )

    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"ERROR: Cannot write report: {exc}", file=sys.stderr)
        return 2

    print(f"Files scanned: {len(files)}")
    print(f"Findings: {len(findings)}")
    print(f"Report: {report_path}")
    print()

    for finding in findings:
        location = finding["file"]
        if finding["line"] is not None:
            location += f":{finding['line']}"

        print(
            f"[{finding['severity']}] "
            f"{location} - {finding['category']}: "
            f"{finding['message']}"
        )

    if not findings:
        print("PASS: No findings detected by these basic checks.")
        return 0

    print()
    print("Review findings manually; these checks are not a full security audit.")

    # Exit 1 means findings exist; exit 2 means analyzer execution failed.
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
