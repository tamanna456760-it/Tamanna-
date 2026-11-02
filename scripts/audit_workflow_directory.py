#!/usr/bin/env python3
"""Read-only inventory and risk review for .github/workflows.

No files are changed, moved, deleted, staged, executed, or committed.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

WORKFLOW_SUFFIXES = {".yml", ".yaml"}
SOURCE_SUFFIXES = {
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh",
    ".bash", ".zsh", ".java", ".kt", ".dart", ".go", ".rs", ".php",
    ".rb", ".c", ".h", ".cpp", ".cs", ".swift", ".bat", ".ps1",
}
CONFIG_SUFFIXES = {
    ".json", ".xml", ".toml", ".ini", ".cfg", ".properties", ".env",
    ".md", ".txt", ".html", ".css",
}
SECRET_PATTERNS = [
    ("github_personal_access_token", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_-]{30,}")),
    ("aws_access_key_id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key_header", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]
RISK_PATTERNS = [
    ("repository_write_command", re.compile(r"\bgit\s+(?:add|commit|push)\b", re.I)),
    ("force_deploy_override", re.compile(r"force[_-]?deploy|continue-on-error\s*:\s*true", re.I)),
    ("pull_request_target_trigger", re.compile(r"pull_request_target\s*:", re.I)),
    ("broad_contents_write", re.compile(r"contents\s*:\s*write", re.I)),
    ("shell_execution", re.compile(r"\b(?:eval|exec)\s*\(", re.I)),
]


def classify(path: Path, text: str | None) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix in WORKFLOW_SUFFIXES:
        if text is None:
            return "yaml-needs-review", "Could not read file as UTF-8"
        lines = text.splitlines()
        has_jobs = any(line.strip() == "jobs:" for line in lines)
        has_on = any(line.strip() == "on:" or line.startswith("on:") for line in lines)
        if has_jobs and has_on:
            return "candidate-github-workflow", "YAML contains on/jobs markers; syntax and action semantics still need validation"
        return "yaml-config-or-invalid-workflow", "YAML extension without both expected on/jobs markers"
    if suffix in SOURCE_SUFFIXES:
        return "source-file-misplaced", "Source-code file in workflow directory; inspect references before moving"
    if suffix in CONFIG_SUFFIXES or not suffix:
        return "config-or-document-misplaced", "Not a GitHub Actions workflow by extension; inspect purpose and references"
    return "other-needs-review", "Unknown file type; manual review required"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(".github/workflows"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root
    if not root.is_dir():
        parser.error(f"directory does not exist or is not a directory: {root}")

    entries = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            text = None
        category, reason = classify(path, text)
        findings = []
        if text is not None:
            for rule, pattern in SECRET_PATTERNS:
                for match in pattern.finditer(text):
                    findings.append({"rule": rule, "line": text.count("\n", 0, match.start()) + 1, "severity": "critical"})
            for rule, pattern in RISK_PATTERNS:
                for match in pattern.finditer(text):
                    findings.append({"rule": rule, "line": text.count("\n", 0, match.start()) + 1, "severity": "high"})
        entries.append({
            "path": path.as_posix(),
            "extension": path.suffix.lower() or "(none)",
            "category": category,
            "reason": reason,
            "bytes": path.stat().st_size,
            "findings": findings,
        })

    summary = {}
    for item in entries:
        summary[item["category"]] = summary.get(item["category"], 0) + 1
    report = {
        "root": root.as_posix(),
        "read_only": True,
        "files_scanned": len(entries),
        "summary": summary,
        "critical_findings": sum(len([f for f in e["findings"] if f["severity"] == "critical"]) for e in entries),
        "high_findings": sum(len([f for f in e["findings"] if f["severity"] == "high"]) for e in entries),
        "files": entries,
        "safety_note": "Findings identify review candidates only. No file is automatically moved, changed, deleted, staged, or executed.",
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
