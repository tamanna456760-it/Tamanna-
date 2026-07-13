#!/usr/bin/env python3
"""
Universal Code Auto‑Fixer – runs language‑specific linters/formatters.
Supports: Python, JS/TS, Go, Rust, C/C++, Java, Ruby, Shell, Markdown, JSON, YAML.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ----------------------------------------------------------------------
# Rich output (optional)
# ----------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

# ----------------------------------------------------------------------
# Language definitions: extensions → fix command templates
# ----------------------------------------------------------------------
LANGUAGE_CONFIGS = {
    ".py": {
        "name": "Python",
        "fixers": [
            {
                "cmd": ["ruff", "check", "--fix", "{file}"],
                "optional": False,
                "dry_run_arg": "--diff",
            },
            {
                "cmd": ["ruff", "format", "{file}"],
                "optional": False,
                "dry_run_arg": "--diff",
            },
        ],
        "extra_fixers": [
            {
                "cmd": ["autoflake", "--in-place", "--remove-all-unused-imports",
                        "--remove-unused-variables", "{file}"],
                "level": "aggressive",
                "dry_run_cmd": ["autoflake", "--check", "--diff", "{file}"],
            }
        ],
        "issue_counter": ["ruff", "check", "{file}", "--statistics"],
    },
    ".js": LANGUAGE_CONFIGS[".js"] = {  # JS and TS share same fixers
        "name": "JavaScript",
        "fixers": [
            {"cmd": ["npx", "eslint", "--fix", "{file}"], "optional": False, "dry_run_arg": "--fix-dry-run"},
            {"cmd": ["npx", "prettier", "--write", "{file}"], "optional": False, "dry_run_arg": "--check"},
        ],
        "issue_counter": ["npx", "eslint", "{file}", "--format=json"],
    },
    ".ts": {
        "name": "TypeScript",
        "fixers": [
            {"cmd": ["npx", "eslint", "--fix", "{file}"], "optional": False, "dry_run_arg": "--fix-dry-run"},
            {"cmd": ["npx", "prettier", "--write", "{file}"], "optional": False, "dry_run_arg": "--check"},
        ],
        "issue_counter": ["npx", "eslint", "{file}", "--format=json"],
    },
    ".go": {
        "name": "Go",
        "fixers": [
            {"cmd": ["goimports", "-w", "{file}"], "optional": False, "dry_run_arg": "-d"},
            {"cmd": ["gofmt", "-w", "{file}"], "optional": False, "dry_run_arg": "-d"},
        ],
        "issue_counter": ["golangci-lint", "run", "--out-format=line-number", "{file}"],
    },
    ".rs": {
        "name": "Rust",
        "fixers": [
            {"cmd": ["rustfmt", "{file}"], "optional": False, "dry_run_arg": "--check"},
        ],
        "issue_counter": ["cargo", "fmt", "--", "--check", "{file}"],  # approximations
    },
    ".c": {
        "name": "C",
        "fixers": [
            {"cmd": ["clang-format", "-i", "{file}"], "optional": False, "dry_run_arg": "--dry-run"},
        ],
        "issue_counter": [],
    },
    ".cpp": {
        "name": "C++",
        "fixers": [
            {"cmd": ["clang-format", "-i", "{file}"], "optional": False, "dry_run_arg": "--dry-run"},
        ],
        "issue_counter": [],
    },
    ".java": {
        "name": "Java",
        "fixers": [
            {"cmd": ["google-java-format", "--replace", "{file}"], "optional": False, "dry_run_arg": "--dry-run"},
        ],
        "issue_counter": [],
    },
    ".rb": {
        "name": "Ruby",
        "fixers": [
            {"cmd": ["rubocop", "-a", "{file}"], "optional": False, "dry_run_arg": "--auto-correct"},
        ],
        "issue_counter": ["rubocop", "--format", "json", "{file}"],
    },
    ".sh": {
        "name": "Shell",
        "fixers": [
            {"cmd": ["shfmt", "-w", "{file}"], "optional": False, "dry_run_arg": "-d"},
        ],
        "issue_counter": [],
    },
    ".md": {
        "name": "Markdown",
        "fixers": [
            {"cmd": ["npx", "prettier", "--write", "{file}"], "optional": False, "dry_run_arg": "--check"},
        ],
        "issue_counter": [],
    },
    ".json": {
        "name": "JSON",
        "fixers": [
            {"cmd": ["npx", "prettier", "--write", "{file}"], "optional": False, "dry_run_arg": "--check"},
        ],
        "issue_counter": [],
    },
    ".yaml": {
        "name": "YAML",
        "fixers": [
            {"cmd": ["npx", "prettier", "--write", "{file}"], "optional": False, "dry_run_arg": "--check"},
        ],
        "issue_counter": [],
    },
    ".yml": {
        "name": "YAML",
        "fixers": [
            {"cmd": ["npx", "prettier", "--write", "{file}"], "optional": False, "dry_run_arg": "--check"},
        ],
        "issue_counter": [],
    },
}

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def run_cmd(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[str, str, int]:
    """Run command, return stdout, stderr, return code."""
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return proc.stdout, proc.stderr, proc.returncode

def tool_available(tool_name: str) -> bool:
    """Check if a tool is in PATH (basic)."""
    return shutil.which(tool_name) is not None or tool_name.startswith("npx")

def count_issues(file_path: Path, config: dict, dry_run: bool = False) -> int:
    """Try to count current issues using language‑specific counter."""
    if not config.get("issue_counter"):
        return 0
    cmd = [c.format(file=file_path) if "{" in c else c for c in config["issue_counter"]]
    _, stderr, code = run_cmd(cmd)
    if code == 0:
        return 0
    # Heuristic: count lines that look like errors (very rough)
    return len([line for line in stderr.splitlines() if "error" in line.lower() or "warning" in line.lower()])

@dataclass
class FixResult:
    path: Path
    success: bool
    language: str
    issues_before: int = 0
    issues_after: int = 0
    errors: List[str] = field(default_factory=list)
    tool_output: str = ""

def fix_file(file_path: Path, level: str, dry_run: bool) -> FixResult:
    """Apply all fixers for the file's language."""
    ext = file_path.suffix
    config = LANGUAGE_CONFIGS.get(ext)
    if not config:
        return FixResult(path=file_path, success=False, language="Unknown",
                         errors=[f"No fixer defined for extension {ext}"])

    issues_before = count_issues(file_path, config, dry_run) if not dry_run else 0
    success = True
    errors = []
    tool_outputs = []

    # Standard fixers
    for fixer in config.get("fixers", []):
        # Skip if fixer is marked for a higher level (e.g., aggressive only)
        if fixer.get("level") == "aggressive" and level != "aggressive" and level != "full":
            continue
        cmd_template = fixer["cmd"]
        if dry_run:
            if "dry_run_arg" in fixer:
                # Replace the last argument (usually the file) with dry-run flag
                dry_cmd = cmd_template[:-1] + [fixer["dry_run_arg"]] + [str(file_path)]
            elif "dry_run_cmd" in fixer:
                dry_cmd = [c.format(file=file_path) for c in fixer["dry_run_cmd"]]
            else:
                dry_cmd = cmd_template + ["--dry-run"]  # fallback
        else:
            dry_cmd = [c.format(file=file_path) if isinstance(c, str) and "{" in c else c for c in cmd_template]
        stdout, stderr, code = run_cmd(dry_cmd)
        tool_outputs.append(stdout + stderr)
        if code != 0 and not dry_run:
            errors.append(f"{cmd_template[0]} failed: {stderr[:200]}")
            success = False

    # Extra aggressive fixers (only for full level)
    if level == "full":
        for extra in config.get("extra_fixers", []):
            if extra.get("level") == "aggressive":
                if dry_run:
                    dry_cmd = extra.get("dry_run_cmd", [c.format(file=file_path) for c in extra["cmd"]])
                else:
                    dry_cmd = [c.format(file=file_path) for c in extra["cmd"]]
                stdout, stderr, code = run_cmd(dry_cmd)
                tool_outputs.append(stdout + stderr)
                if code != 0 and not dry_run:
                    errors.append(f"{extra['cmd'][0]} failed: {stderr[:200]}")
                    success = False

    issues_after = count_issues(file_path, config, dry_run) if not dry_run else 0
    return FixResult(
        path=file_path,
        success=success,
        language=config["name"],
        issues_before=issues_before,
        issues_after=issues_after,
        errors=errors,
        tool_output="\n---\n".join(tool_outputs)
    )

# ----------------------------------------------------------------------
# Main orchestration
# ----------------------------------------------------------------------
def collect_files(paths: List[str]) -> List[Path]:
    files = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(path.rglob("*"))
    # Keep only files with supported extensions
    supported_exts = set(LANGUAGE_CONFIGS.keys())
    return [f for f in files if f.suffix in supported_exts]

def print_report(report_data: dict, dry_run: bool, console):
    total_files = report_data["total_files"]
    success = report_data["successful"]
    failed = report_data["failed"]
    fixed_issues = report_data["total_issues_fixed"]
    results = report_data["results"]

    if RICH_AVAILABLE and console:
        table = Table(title="Auto‑Fix Report (All Languages)", show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Lang")
        table.add_column("Status")
        table.add_column("Before")
        table.add_column("After")
        table.add_column("Fixed")
        for r in results:
            fixed = r["issues_before"] - r["issues_after"]
            table.add_row(
                r["path"], r["language"],
                "✅" if r["success"] else "❌",
                str(r["issues_before"]),
                str(r["issues_after"]),
                str(fixed)
            )
        console.print(table)
        console.print(Panel(
            f"[bold]Total files:[/] {total_files}\n"
            f"[green]✅ Successful:[/] {success}\n"
            f"[red]❌ Failed:[/] {failed}\n"
            f"[yellow]📊 Total issues fixed:[/] {fixed_issues}",
            title="Summary"
        ))
    else:
        print("\n" + "="*60)
        print("AUTO‑FIX REPORT (All Languages)")
        print("="*60)
        for r in results:
            fixed = r["issues_before"] - r["issues_after"]
            status = "OK" if r["success"] else "FAIL"
            print(f"{status:4} {r['path']} ({r['language']}): {r['issues_before']} → {r['issues_after']} (fixed {fixed})")
            if r["errors"]:
                print(f"     Errors: {', '.join(r['errors'][:2])}")
        print("-"*60)
        print(f"Total: {total_files} files, {success} succeeded, {failed} failed")
        print(f"Issues fixed: {fixed_issues}")

# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Universal code auto‑fixer for many languages.")
    parser.add_argument("paths", nargs="+", help="Files/directories to fix")
    parser.add_argument("--level", choices=["safe", "aggressive", "full"], default="safe",
                        help="safe=standard fixes, aggressive=+unused imports, full=+extra cleaners")
    parser.add_argument("--dry-run", action="store_true", help="Show diff, no changes")
    parser.add_argument("--jobs", type=int, default=4, help="Parallel workers")
    parser.add_argument("--json-report", type=Path, help="Export JSON report")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress bar")
    args = parser.parse_args()

    files = collect_files(args.paths)
    if not files:
        print("No supported files found.")
        sys.exit(1)

    console = Console() if RICH_AVAILABLE and not args.no_progress else None
    results = []
    import time
    start = time.time()

    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(fix_file, f, args.level, args.dry_run): f for f in files}
        if console:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          transient=True, console=console) as progress:
                task = progress.add_task("[cyan]Fixing files...", total=len(files))
                for future in as_completed(futures):
                    res = future.result()
                    results.append(res)
                    progress.update(task, advance=1)
        else:
            for future in as_completed(futures):
                res = future.result()
                results.append(res)
                print(f"\rProcessed {len(results)}/{len(files)}", end="")
            print()

    end = time.time()
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    total_fixed = sum(max(0, r.issues_before - r.issues_after) for r in results)

    report_dict = {
        "total_files": len(results),
        "successful": successful,
        "failed": failed,
        "total_issues_fixed": total_fixed,
        "duration_sec": end - start,
        "results": [
            {
                "path": str(r.path),
                "language": r.language,
                "success": r.success,
                "issues_before": r.issues_before,
                "issues_after": r.issues_after,
                "errors": r.errors,
            }
            for r in results
        ]
    }

    print_report(report_dict, args.dry_run, console)
    if args.json_report:
        args.json_report.write_text(json.dumps(report_dict, indent=2))
        print(f"📄 Report saved to {args.json_report}")

    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()