
#!/usr/bin/env python3
"""Tamanna AI repository repair auditor.

Safe by default:
- Does not overwrite project files.
- Does not push commits.
- Writes a Markdown audit report only.
"""

from pathlib import Path
import re
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
REPORT = ROOT / "tamanna_repair_report.md"

RISK_PATTERNS = [
    ("CRITICAL", r"git\s+push\s+--mirror"),
    ("HIGH", r"git\s+push\s+.*--force"),
    ("HIGH", r"git\s+add\s+\.\s*(?:&&|;|\n).*git\s+commit"),
    ("HIGH", r"contents:\s*write"),
    ("HIGH", r"pull_request_target"),
    ("HIGH", r"\$\{\{\s*github\.event\.(?:comment\.body|issue\.title|issue\.body)"),
    ("MEDIUM", r"continue-on-error:\s*true"),
    ("MEDIUM", r"actions/upload-artifact@v[123]\b"),
    ("MEDIUM", r"uses:\s*[^#\s]+@(main|master)\b"),
    ("MEDIUM", r"find\s+\.\s+-name\s+[\"']?\*\.py"),
    ("MEDIUM", r"placeholder"),
    ("MEDIUM", r"OPENAI_API_KEY"),
]

SCRIPT_RE = re.compile(
    r"""(?:python(?:3)?|py)\s+["']?([A-Za-z0-9_./-]+\.py)"""
)

def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f""

def main():
    findings = []
    workflow_count = 0
    script_count = 0

    if not WORKFLOWS.exists():
        findings.append((
            "HIGH", ".github/workflows",
            "Workflow directory not found."
        ))
    else:
        workflow_files = sorted(
            p for p in WORKFLOWS.rglob("*")
            if p.is_file()
        )

        for path in workflow_files:
            rel = path.relative_to(ROOT).as_posix()

            if path.suffix.lower() not in (".yml", ".yaml"):
                findings.append((
                    "LOW", rel,
                    "Non-YAML file is inside the workflows directory; "
                    "review whether it belongs elsewhere."
                ))
                continue

            workflow_count += 1
            content = read_text(path)

            # Find scripts referenced in commands.
            for match in SCRIPT_RE.finditer(content):
                target = match.group(1)
                if "$" in target or "${{" in target:
                    continue
                candidate = (ROOT / target).resolve()
                try:
                    candidate.relative_to(ROOT.resolve())
                except ValueError:
                    findings.append((
                        "HIGH", rel,
                        f"Script path escapes repository: {target}"
                    ))
                    continue

                if not candidate.is_file():
                    findings.append((
                        "HIGH", rel,
                        f"Referenced Python script is missing: {target}"
                    ))

            for severity, pattern in RISK_PATTERNS:
                if re.search(pattern, content, flags=re.IGNORECASE):
                    findings.append((
                        severity, rel,
                        f"Review required for pattern: {pattern}"
                    ))

            # A quick YAML syntax check when PyYAML is installed.
            try:
                import yaml
                class UniqueKeyLoader(yaml.SafeLoader):
                    pass

                def construct_mapping(loader, node, deep=False):
                    mapping = {}
                    for key_node, value_node in node.value:
                        key = loader.construct_object(key_node, deep=deep)
                        if key in mapping:
                            raise ValueError(
                                f"Duplicate YAML key: {key!r}"
                            )
                        mapping[key] = loader.construct_object(
                            value_node, deep=deep
                        )
                    return mapping

                UniqueKeyLoader.add_constructor(
                    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                    construct_mapping,
                )
                yaml.load(content, Loader=UniqueKeyLoader)
            except ImportError:
                pass
            except Exception as exc:
                findings.append((
                    "HIGH", rel, f"YAML validation failed: {exc}"
                ))

    # Check that the key project entry points exist.
    for relative in (
        "README.md",
        "scripts/analyzer.py",
        "scripts/fixer.py",
        ".github/workflows/analyzer.yml",
    ):
        if not (ROOT / relative).is_file():
            findings.append((
                "HIGH", relative, "Expected project file is missing."
            ))

    # Report Python source count without executing project scripts.
    for path in ROOT.rglob("*.py"):
        if any(part in {
            ".git", ".venv", "venv", "node_modules", "__pycache__"
        } for part in path.parts):
            continue
        script_count += 1

    rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    findings.sort(key=lambda item: (rank[item[0]], item[1], item[2]))

    lines = [
        "# Tamanna AI — Repository Repair Audit",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Repository: `{ROOT.name}`",
        f"- Workflow YAML files inspected: {workflow_count}",
        f"- Python files counted (not executed): {script_count}",
        f"- Findings: {len(findings)}",
        "",
        "> Audit-only mode. No source files were changed and no commits "
        "were pushed.",
        "",
        "## Findings",
        "",
    ]

    if not findings:
        lines.append("No configured checks reported a finding.")
    else:
        for severity, path, message in findings:
            lines.append(f"- **{severity}** `{path}` — {message}")

    lines += [
        "",
        "## Recommended remediation order",
        "",
        "1. Disable or convert unsafe direct-to-main auto-repair workflows.",
        "2. Remove force-push mirror actions unless explicitly required.",
        "3. Fix missing script references and validate YAML syntax.",
        "4. Replace untrusted issue/comment interpolation in shell commands.",
        "5. Pin third-party actions to reviewed release tags or commit SHAs.",
        "6. Make tests fail visibly; avoid masking failures with `|| true`.",
        "7. Run tests and review a branch/PR before merging to main.",
        "",
    ]

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Audit complete. Findings: {len(findings)}")
    print(f"Report: {REPORT}")
    return 1 if any(x[0] in {"CRITICAL", "HIGH"} for x in findings) else 0

if __name__ == "__main__":
    sys.exit(main())
