#!/usr/bin/env python3
"""
Tamanna AI System – Unified Security Scanner
---------------------------------------------
Package: TamannaAISystem
Version: 2.0.0
Target: cross-platform (Linux, macOS, Windows)
UID: auto-generated per run (or based on system)
Making: Tamanna AI Team | Build 2025-04-12
"""

import os
import sys
import re
import json
import uuid
import platform
import datetime
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple

# ============================================================================
# METADATA (Package info, version, target, UID, making)
# ============================================================================
PACKAGE_NAME = "TamannaAISystem"
VERSION = "2.0.0"
TARGET = platform.system() + " " + platform.release()
UID = str(uuid.uuid4())  # unique ID for this run
MAKING = {
    "author": "Tamanna AI Team",
    "build_date": datetime.date.today().isoformat(),
    "description": "Unified threat simulation, code scanner, and Git config auditor",
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def print_banner():
    """Display system banner with metadata."""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                  {PACKAGE_NAME} v{VERSION}                      ║
║   Target: {TARGET:<48}║
║   Run UID: {UID:<47}║
║   Build: {MAKING['build_date']} | {MAKING['author']:<30}║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


# ============================================================================
# 1) THREAT SIMULATION (from earlier HTML version, adapted to CLI)
# ============================================================================
THREAT_CATALOG = [
    {"name": "SQL Injection Attempt", "severity": 85, "type": "critical"},
    {"name": "Cross-Site Scripting (XSS)", "severity": 78, "type": "high"},
    {"name": "Privilege Escalation", "severity": 92, "type": "critical"},
    {"name": "Malicious File Upload", "severity": 76, "type": "high"},
    {"name": "Suspicious API Call", "severity": 38, "type": "medium"},
    {"name": "Unusual Outbound Traffic", "severity": 60, "type": "medium"},
    {"name": "Weak Encryption Detected", "severity": 30, "type": "low"},
    {"name": "Missing Security Headers", "severity": 25, "type": "low"},
]

import random
import time


def run_threat_simulation():
    """Simulate an AI threat detection scan."""
    print("\n[🎭] Running Threat Simulation...")
    input("Press Enter to start the scan...")
    print("Scanning", end="", flush=True)
    for _ in range(10):
        time.sleep(0.2)
        print(".", end="", flush=True)
    print("\n")
    num_threats = random.randint(2, 5)
    threats = []
    for _ in range(num_threats):
        t = random.choice(THREAT_CATALOG)
        score = t["severity"] + random.randint(-8, 8)
        score = max(0, min(100, score))
        threats.append({"name": t["name"], "score": score, "type": t["type"]})
    threats.sort(key=lambda x: x["score"], reverse=True)
    overall_risk = sum(t["score"] for t in threats) // len(threats)
    print(f"📊 Overall Risk Score: {overall_risk}%")
    print("Detected threats:")
    for t in threats:
        print(f"  ⚠️ {t['name']} – risk {t['score']}%")
    print("\n✅ Simulation complete.\n")


# ============================================================================
# 2) CODE SCANNER (static analysis of local files)
# ============================================================================
DEFAULT_RULES = [
    (
        re.compile(r'password\s*=\s*[\'"].+[\'"]', re.I),
        "critical",
        "Hardcoded password",
    ),
    (re.compile(r'api_key\s*=\s*[\'"].+[\'"]', re.I), "critical", "Hardcoded API key"),
    (re.compile(r"eval\s*\(", re.I), "high", "Use of eval() – code injection risk"),
    (
        re.compile(r"document\.write\s*\(", re.I),
        "medium",
        "document.write can lead to XSS",
    ),
    (re.compile(r"innerHTML\s*=", re.I), "medium", "innerHTML may cause XSS"),
    (re.compile(r"exec\s*\(", re.I), "high", "Arbitrary command execution"),
    (re.compile(r"system\s*\(", re.I), "high", "System call – command injection risk"),
    (
        re.compile(r"\.sql\s*\+", re.I),
        "medium",
        "String concatenation SQL – possible injection",
    ),
]


def scan_file(file_path: Path) -> Dict[str, Any]:
    """Scan a single file for security issues."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"file": str(file_path), "error": "Cannot read file"}
    issues = []
    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        for pattern, risk, msg in DEFAULT_RULES:
            if pattern.search(line):
                issues.append(
                    {
                        "line": idx,
                        "risk": risk,
                        "message": msg,
                        "snippet": line.strip()[:80],
                    }
                )
    risk_score = 0
    risk_map = {"critical": 100, "high": 70, "medium": 40, "low": 15}
    for issue in issues:
        score = risk_map.get(issue["risk"], 0)
        if score > risk_score:
            risk_score = score
    return {"file": str(file_path), "issues": issues, "risk_score": risk_score}


def run_code_scanner(paths: List[str]):
    """Scan user‑provided files/directories."""
    print("\n[📁] Code Scanner – Static Security Analysis")
    if not paths:
        print("No files specified. Use --files or --dir to scan.")
        return
    files_to_scan = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files_to_scan.extend(path.rglob("*.py"))
            files_to_scan.extend(path.rglob("*.js"))
            files_to_scan.extend(path.rglob("*.html"))
            files_to_scan.extend(path.rglob("*.java"))
            files_to_scan.extend(path.rglob("*.c"))
            files_to_scan.extend(path.rglob("*.cpp"))
        elif path.is_file():
            files_to_scan.append(path)
        else:
            print(f"⚠️ Path not found: {p}")
    if not files_to_scan:
        print("No supported files found.")
        return
    print(f"Scanning {len(files_to_scan)} file(s)...")
    results = []
    for f in files_to_scan:
        res = scan_file(f)
        results.append(res)
    # Display results
    for res in results:
        risk = res.get("risk_score", 0)
        risk_label = (
            "CRITICAL"
            if risk >= 70
            else ("HIGH" if risk >= 40 else ("MEDIUM" if risk >= 20 else "LOW"))
        )
        print(f"\n📄 {res['file']} – Risk: {risk}% ({risk_label})")
        if res.get("issues"):
            for iss in res["issues"]:
                print(f"   Line {iss['line']}: {iss['message']}")
                print(f"     → {iss['snippet']}")
        else:
            print("   ✅ No issues found.")
    print("\n✅ Code scan completed.\n")


# ============================================================================
# 3) GIT CONFIG AUDITOR (checks .git/config best practices)
# ============================================================================
GIT_BEST_PRACTICES = [
    (
        "core",
        "autocrlf",
        "input",
        "medium",
        "Set core.autocrlf = input to prevent CRLF issues.",
    ),
    (
        "core",
        "safecrlf",
        "warn",
        "low",
        "Enable core.safecrlf to warn about CRLF changes.",
    ),
    ("core", "fsmonitor", "true", "low", "Enable core.fsmonitor for faster status."),
    (
        "core",
        "untrackedCache",
        "true",
        "low",
        "core.untrackedCache speeds up git status.",
    ),
    (
        "core",
        "preloadIndex",
        "true",
        "low",
        "Enable core.preloadIndex for parallel index loading.",
    ),
    (
        "http",
        "postBuffer",
        "524288000",
        "medium",
        "Increase http.postBuffer to at least 500MB for large pushes.",
    ),
    (
        "http",
        "sslVerify",
        "true",
        "critical",
        "http.sslVerify must be true to prevent MITM attacks.",
    ),
    (
        'remote "origin"',
        "prune",
        "true",
        "low",
        "Set remote.origin.prune = true to auto‑prune stale branches.",
    ),
    (
        "fetch",
        "prune",
        "true",
        "low",
        "fetch.prune = true auto‑removes remote‑tracking branches.",
    ),
    ("pull", "rebase", "true", "medium", "pull.rebase = true keeps history linear."),
    (
        "push",
        "default",
        "simple",
        "medium",
        "push.default = simple prevents accidental multi‑branch pushes.",
    ),
    (
        "rebase",
        "autoStash",
        "true",
        "low",
        "rebase.autoStash = true automatically stashes changes before rebase.",
    ),
    (
        "merge",
        "conflictStyle",
        "zdiff3",
        "low",
        "merge.conflictStyle = zdiff3 gives better conflict markers.",
    ),
]


def parse_git_config(content: str) -> Dict[str, Dict[str, str]]:
    """Parse a .git/config style content into a nested dict."""
    config = {}
    current_section = None
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            config[current_section] = {}
        elif "=" in line and current_section:
            key, value = line.split("=", 1)
            config[current_section][key.strip()] = value.strip()
    return config


def audit_git_config(config_path: Path = None):
    """Audit a Git config file (defaults to .git/config in current directory)."""
    print("\n[⚙️] Git Config Auditor")
    if config_path is None:
        config_path = Path.cwd() / ".git" / "config"
    if not config_path.exists():
        print(
            f"Git config not found at {config_path}. Please run inside a Git repository."
        )
        return
    content = config_path.read_text(encoding="utf-8")
    parsed = parse_git_config(content)
    findings = []
    for section, key, recommended, risk, message in GIT_BEST_PRACTICES:
        sec_data = parsed.get(section)
        if sec_data is None:
            findings.append(
                (
                    risk,
                    section,
                    key,
                    f"Missing section [{section}]",
                    f"Add [{section}] with {key}={recommended}",
                )
            )
            continue
        actual = sec_data.get(key)
        if actual is None:
            findings.append(
                (risk, section, key, f"Missing key {key}", f"Set {key}={recommended}")
            )
        elif str(actual).lower() != str(recommended).lower():
            findings.append(
                (
                    risk,
                    section,
                    key,
                    f"Misconfigured: found '{actual}', expected '{recommended}'",
                    f"Change {key} to {recommended}",
                )
            )
        else:
            findings.append(("ok", section, key, "", ""))
    # Additional check: remote URL should be HTTPS
    if 'remote "origin"' in parsed and "url" in parsed['remote "origin"']:
        url = parsed['remote "origin"']["url"]
        if url.startswith("git@") or url.startswith("git://"):
            findings.append(
                (
                    "high",
                    'remote "origin"',
                    "url",
                    f"Uses non‑HTTPS: {url}",
                    "Change to HTTPS URL",
                )
            )
    # Display summary
    critical = high = medium = low = 0
    for risk, _, _, _, _ in findings:
        if risk == "critical":
            critical += 1
        elif risk == "high":
            high += 1
        elif risk == "medium":
            medium += 1
        elif risk == "low":
            low += 1
    print(
        f"📊 Audit summary: {critical} critical, {high} high, {medium} medium, {low} low issues."
    )
    for risk, section, key, msg, fix in findings:
        if risk == "ok":
            continue
        risk_label = risk.upper()
        print(f"\n[{risk_label}] {section} → {key}")
        print(f"    {msg}")
        print(f"    🔧 Fix: {fix}")
    print("\n✅ Audit complete.\n")


# ============================================================================
# MAIN CLI DISPATCHER
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=f"{PACKAGE_NAME} v{VERSION} – Unified Security Scanner"
    )
    parser.add_argument("--simulate", action="store_true", help="Run threat simulation")
    parser.add_argument(
        "--scan", nargs="+", help="Scan files/directories for security issues"
    )
    parser.add_argument(
        "--git-audit", action="store_true", help="Audit current Git repository config"
    )
    parser.add_argument("--info", action="store_true", help="Show system metadata only")
    args = parser.parse_args()

    print_banner()

    if args.info:
        return

    if not (args.simulate or args.scan or args.git_audit):
        print(
            "No action specified. Use --simulate, --scan, or --git-audit. See --help."
        )
        return

    if args.simulate:
        run_threat_simulation()
    if args.scan:
        run_code_scanner(args.scan)
    if args.git_audit:
        audit_git_config()


if __name__ == "__main__":
    main()
