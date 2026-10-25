#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / ".tamanna-repair-backup" / STAMP

AI_DEBUG = r'''name: Tamanna AI Debug
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  debug:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
          submodules: false

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install check tools
        run: python -m pip install pytest flake8

      - name: Check helper syntax
        run: python -m py_compile scripts/analyzer.py scripts/fixer.py

      - name: Lint helper files
        run: flake8 scripts/analyzer.py scripts/fixer.py

      - name: Run read-only analyzer
        env:
          TAMANNA_ANALYZER_REPORT: ${{ runner.temp }}/tamanna_analyzer_report.json
        run: python scripts/analyzer.py

      - name: Create review-only fix plan
        env:
          TAMANNA_ANALYZER_REPORT: ${{ runner.temp }}/tamanna_analyzer_report.json
          TAMANNA_FIXER_REPORT: ${{ runner.temp }}/tamanna_fix_plan.json
        run: python scripts/fixer.py

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: tamanna-ai-debug-reports
          path: |
            ${{ runner.temp }}/tamanna_analyzer_report.json
            ${{ runner.temp }}/tamanna_fix_plan.json
          if-no-files-found: warn
          retention-days: 14
'''

SECURITY = r'''name: Tamanna Security Checks
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: "0 0 * * 0"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  security-audit:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install security tools
        run: |
          python -m pip install --upgrade pip
          python -m pip install bandit pip-audit detect-secrets

      - name: Scan Python code
        shell: bash
        run: |
          set -euo pipefail
          paths=()
          for path in scripts runner/python; do
            if [ -d "$path" ]; then paths+=("$path"); fi
          done
          if [ "${#paths[@]}" -gt 0 ]; then
            bandit -r "${paths[@]}" -f json -o bandit-report.json
          else
            echo '{"results":[]}' > bandit-report.json
          fi

      - name: Audit Python dependencies
        shell: bash
        run: |
          set -euo pipefail
          if [ -f requirements.txt ]; then
            pip-audit -r requirements.txt -f json -o pip-audit-report.json
          else
            echo '{"dependencies":[]}' > pip-audit-report.json
          fi

      - name: Scan tracked files for secret patterns
        run: detect-secrets scan --all-files > detect-secrets-report.json

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: tamanna-security-reports
          path: |
            bandit-report.json
            pip-audit-report.json
            detect-secrets-report.json
          if-no-files-found: warn
          retention-days: 14
'''

READ_ONLY_UPGRADE = r'''name: Tamanna AI Upgrade Review
on:
  workflow_dispatch:
  pull_request:
    branches: [main]

permissions:
  contents: read
  pull-requests: read

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Validate repository whitespace
        run: git diff --check

      - name: Validate helper syntax
        run: |
          for file in scripts/analyzer.py scripts/fixer.py; do
            if [ -f "$file" ]; then python -m py_compile "$file"; fi
          done

      - name: Explain review-only mode
        run: |
          echo "No AI source upload, file rewrite, branch creation, or auto-merge."
          echo "Proposed upgrades must be reviewed in a pull request."
'''

READ_ONLY_SYNC = r'''name: BD-KING-R7 PowerHub Safe Audit
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
          submodules: false

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Check whitespace
        run: git diff --check

      - name: Check helper syntax
        run: |
          for file in scripts/analyzer.py scripts/fixer.py scripts/tamanna_repo_repair.py; do
            if [ -f "$file" ]; then python -m py_compile "$file"; fi
          done

      - name: Report build inputs
        run: |
          for file in package.json requirements.txt go.mod Cargo.toml Makefile build.sh; do
            if [ -f "$file" ]; then echo "Found: $file"; fi
          done
          echo "Read-only audit; no formatting or push performed."
'''

RADAR = r'''#!/usr/bin/env python3
"""Tamanna Radar: read-only file inventory and suspicious-pattern scanner."""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules",
    "__pycache__", ".pytest_cache", "dist", "build"
}
SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".json", ".sh", ".bat", ".cmd",
    ".ps1", ".vbs", ".php", ".html", ".yml", ".yaml", ".env"
}
KEYWORDS = [
    "os.system(", "subprocess.", "eval(", "exec(",
    "rm -rf", "chmod 777", "nc -e", "powershell -enc",
    "-----begin private key-----"
]


def sha256_hash(path):
    digest = hashlib.sha256()
    try:
        with Path(path).open("rb") as stream:
            for chunk in iter(lambda: stream.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError as exc:
        return f"Hash Error: {exc}"


def analyze_code(path):
    try:
        if Path(path).stat().st_size > 2_000_000:
            return ["Text scan skipped: file exceeds 2 MB"]
        content = Path(path).read_text(
            encoding="utf-8", errors="ignore"
        ).lower()
        return [word for word in KEYWORDS if word in content]
    except OSError as exc:
        return [f"Read Error: {exc}"]


def scan_directory(target):
    results = []
    for root, dirs, files in os.walk(target, followlinks=False):
        dirs[:] = sorted(
            name for name in dirs
            if name not in SKIP_DIRS and not name.startswith(".git")
        )
        for name in sorted(files):
            path = Path(root) / name
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                findings = (
                    analyze_code(path)
                    if path.suffix.lower() in SCAN_EXTENSIONS else []
                )
                results.append({
                    "file": str(path.resolve()),
                    "extension": path.suffix.lower(),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_hash(path),
                    "suspicious_keywords": findings,
                    "requires_human_review": bool(findings),
                })
            except OSError as exc:
                results.append({"file": str(path), "error": str(exc)})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--output", default="tamanna_radar_report.json")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        parser.error(f"Not a directory: {target}")

    results = scan_directory(target)
    report = {
        "scanner": "Tamanna Radar",
        "scan_time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "target": str(target),
        "total_results": len(results),
        "files_with_findings": sum(
            bool(item.get("suspicious_keywords")) for item in results
        ),
        "results": results,
        "note": "Pattern matches need human review; they do not prove malware."
    }
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\\n",
        encoding="utf-8"
    )
    print(f"Files inventoried: {len(results)}")
    print(f"Report: {output}")


if __name__ == "__main__":
    main()
'''

SIGNAL = r'''"""Tamanna defensive event helpers; no external actions are taken."""


def detect_intrusion(event):
    text = str(event).lower()
    markers = (
        "unauthorized", "failed_login", "strange_ip", "file_change"
    )
    return any(marker in text for marker in markers)


def tamanna_defense(event):
    if detect_intrusion(event):
        return "Tamanna: সতর্ক! সন্দেহজনক কার্যকলাপ ধরা পড়েছে."
    return "Tamanna: সব ঠিক আছে, সিস্টেম শান্ত."


if __name__ == "__main__":
    print(tamanna_defense("failed_login from unknown IP"))
'''

DEEP_POWER = r'''"""Tamanna symbolic state and synchronization helpers."""


class TamannaDeepPower:
    def __init__(self):
        self.state = "calm"
        self.energy = 1.0
        self.memory = []

    def log(self, event, detail):
        entry = {"event": event, "detail": detail}
        self.memory.append(entry)

    def boost_energy(self, pressure):
        self.energy = round(self.energy + float(pressure) * 0.1, 2)
        self.log("energy_boost", f"Energy now {self.energy}")
        return self.energy

    def set_state(self, new_state):
        self.state = str(new_state)
        self.log("state_change", self.state)

    def heartbeat(self):
        self.log("heartbeat", f"State: {self.state}")

    def react(self, signal):
        mapping = {
            "ok": "calm", "warn": "alert", "error": "pain",
            "recover": "healing"
        }
        self.set_state(mapping.get(signal, "unknown"))
        return self.state


class SyncPower:
    def __init__(self):
        self.emotion = "calm"
        self.intel_state = "idle"
        self.memory = []

    def log(self, kind, detail):
        self.memory.append({"kind": kind, "detail": detail})

    def heartbeat(self):
        self.log("heartbeat", f"emotion={self.emotion}, intel={self.intel_state}")

    def sync_emotion(self, signal):
        mapping = {"ok": "calm", "warn": "alert", "error": "pain", "deep": "focused"}
        self.emotion = mapping.get(signal, "unknown")
        self.log("emotion_update", self.emotion)

    def sync_intelligence(self, signal):
        mapping = {"ok": "stable", "warn": "monitoring", "error": "critical", "deep": "deep_mode"}
        self.intel_state = mapping.get(signal, "unknown")
        self.log("intel_update", self.intel_state)

    def sync(self, signal):
        self.sync_emotion(signal)
        self.sync_intelligence(signal)
        self.heartbeat()


class TamannaUnifiedCore:
    def __init__(self):
        self.emotion = "calm"
        self.intel = "idle"
        self.sync_state = "normal"
        self.memory = []

    def log(self, kind, detail):
        self.memory.append({"kind": kind, "detail": detail})

    def update_emotion(self, signal):
        mapping = {"ok": "calm", "warn": "alert", "error": "pain", "deep": "focused"}
        self.emotion = mapping.get(signal, "unknown")
        self.log("emotion", self.emotion)

    def update_intel(self, signal):
        mapping = {"ok": "stable", "warn": "monitoring", "error": "critical", "deep": "deep_mode"}
        self.intel = mapping.get(signal, "unknown")
        self.log("intelligence", self.intel)

    def sync_pulse(self):
        self.log("pulse", f"emotion={self.emotion}, intel={self.intel}, mode={self.sync_state}")

    def sync(self, signal):
        self.update_emotion(signal)
        self.update_intel(signal)
        self.sync_state = (
            "deep_sync" if signal == "deep"
            else "defense_sync" if signal == "error"
            else "normal"
        )
        self.log("sync_state", self.sync_state)
        self.sync_pulse()


class TamannaPowerExpansion:
    def __init__(self):
        self.emotion = "calm"
        self.intel = "stable"
        self.sync = "normal"
        self.energy = 1.0

    def log(self, kind, detail):
        print("⚡", kind, "→", detail)

    def pulse(self):
        self.log("pulse", f"emotion={self.emotion}, intel={self.intel}, sync={self.sync}, energy={self.energy}")

    def amplify(self):
        self.energy = round(self.energy * 1.2, 2)
        self.log("amplify", f"energy boosted to {self.energy}")
        return self.energy

    def shift(self, signal):
        if signal == "deep":
            self.emotion, self.intel, self.sync = "focused", "deep_mode", "deep_sync"
            self.amplify()
        elif signal == "warn":
            self.emotion, self.intel, self.sync = "alert", "monitoring", "defense_sync"
        elif signal == "error":
            self.emotion, self.intel, self.sync = "pain", "critical", "defense_sync"
        else:
            self.emotion, self.intel, self.sync = "calm", "stable", "normal"
        self.pulse()
        return {
            "emotion": self.emotion, "intel": self.intel,
            "sync": self.sync, "energy": self.energy
        }
'''


def backup(path):
    destination = BACKUP / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)


def replace_file(relative, content, apply, results):
    path = ROOT / relative
    if not path.exists():
        results.append({"file": relative, "status": "missing"})
        return
    old = path.read_text(encoding="utf-8")
    if old == content + "\n":
        results.append({"file": relative, "status": "already_current"})
        return
    results.append({
        "file": relative,
        "status": "changed" if apply else "would_change"
    })
    if apply:
        backup(path)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")


def repair_tamanna_ai(apply, results):
    relative = "runner/python/tamanna_ai.py"
    path = ROOT / relative
    if not path.exists():
        results.append({"file": relative, "status": "missing"})
        return
    text = path.read_text(encoding="utf-8")
    updated = text

    if not updated.startswith('"""'):
        updated = '"""\n' + updated

    junk = [
        "bd-king-r7.io", "google.py", "API.py", "tamanna_update.py",
        "test_commands.py", "tamanna.text", "auto_committer.js",
        "main.js", "setup.js", "p_monitor.py", "network_monitoring.py",
        "API_api.py", "system_monitoring.py", "config.py", "stml-core.js",
        "tamanna_ai_apps.js", "domen.py", "insan_tamanna.py",
        "uptime_monitor.py", "bdkingr7.py", "bd.king.r7.py",
        "hminsun23@gmail.com.py", "gmail.py", "tamanna_uility.py"
    ]
    for name in junk:
        updated = updated.replace('"' + name + '"\n', "")

    updated = updated.replace(
        '        self.load_memory =\n"tamanna456760-it"',
        "        self.load_memory()"
    )

    # If the malformed assignment is absent, load memory after audio setup.
    if "self.load_memory()" not in updated[:updated.find("    def load_memory")]:
        updated = updated.replace(
            "        self.microphone = sr.Microphone()\n",
            "        self.microphone = sr.Microphone()\n        self.load_memory()\n",
            1
        )

    if "import shlex" not in updated:
        updated = updated.replace("import subprocess\n", "import subprocess\nimport shlex\n", 1)

    updated = updated.replace(
        'self.execute_command("nmap --help | head -20")',
        'self.execute_command("nmap --help")'
    )
    updated = updated.replace(
        'self.execute_command("sudo apt update")',
        '"সিস্টেম আপডেটের আগে অনুমতি নিয়ে টার্মিনালে sudo apt update চালান।"'
    )
    updated = updated.replace("                command,\n                shell=True,", "                shlex.split(command),\n                shell=False,")

    if 'if __name__ == "__main__":' not in updated:
        updated += '\n\nif __name__ == "__main__":\n    main()\n'

    if updated == text:
        results.append({"file": relative, "status": "no_change_review_manually"})
        return
    results.append({
        "file": relative,
        "status": "changed" if apply else "would_change"
    })
    if apply:
        backup(path)
        path.write_text(updated, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not (ROOT / ".git").exists():
        print("STOP: Run this from the root of the cloned Git repository.")
        return 2

    results = []
    files = {
        ".github/workflows/ai-debug.yml": AI_DEBUG,
        ".github/workflows/security-checks.yml": SECURITY,
        ".github/workflows/auto-upgrade.yml": READ_ONLY_UPGRADE,
        ".github/workflows/auto-sync-bd-king-r7.yml": READ_ONLY_SYNC,
        "runner/python/radar.py": RADAR,
        "runner/python/signal.py": SIGNAL,
        "runner/python/tamanna_deep_power.py": DEEP_POWER,
    }
    for relative, content in files.items():
        replace_file(relative, content, args.apply, results)

    repair_tamanna_ai(args.apply, results)

    report = {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry-run",
        "backup": str(BACKUP) if args.apply else None,
        "results": results,
        "github_push_performed": False
    }
    report_path = ROOT / "tamanna_remaining_repair_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    for item in results:
        print(f"{item['status']}: {item['file']}")
    print(f"Report: {report_path}")
    if args.apply:
        print(f"Backup: {BACKUP}")
    else:
        print("Dry run only. If the proposed changes are acceptable, rerun with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY

python3 -m py_compile scripts/tamanna_finish_repair.py
python3 scripts/tamanna_finish_repair.py
