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

RADAR = r'''"""Tamanna Radar: read-only file inventory and keyword scanner."""
import argparse
import hashlib
import json
import os
from pathlib import Path

SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}
EXTENSIONS = {".py", ".js", ".ts", ".json", ".sh", ".yml", ".yaml", ".html"}
KEYWORDS = ("os.system(", "subprocess.", "eval(", "exec(", "rm -rf",
            "chmod 777", "nc -e", "-----begin private key-----")


def sha256_hash(file_path):
    digest = hashlib.sha256()
    try:
        with Path(file_path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError as exc:
        return f"Hash Error: {exc}"


def analyze_code(file_path):
    try:
        if Path(file_path).stat().st_size > 2_000_000:
            return ["Skipped: file exceeds 2 MB"]
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore").lower()
        return [word for word in KEYWORDS if word in text]
    except OSError as exc:
        return [f"Read Error: {exc}"]


def scan_directory(target_dir):
    results = []
    for root, dirs, files in os.walk(target_dir, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith(".git")]
        for name in sorted(files):
            path = Path(root) / name
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                findings = analyze_code(path) if path.suffix.lower() in EXTENSIONS else []
                results.append({
                    "file": str(path),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_hash(path),
                    "suspicious_keywords": findings,
                    "requires_review": bool(findings),
                })
            except OSError as exc:
                results.append({"file": str(path), "error": str(exc)})
    return results


def main():
    parser = argparse.ArgumentParser(description="Tamanna read-only file scanner")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--output", default="tamanna_radar_report.json")
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        parser.error(f"Not a directory: {target}")
    results = scan_directory(target)
    report = {
        "scanner": "Tamanna Radar",
        "target": str(target),
        "total_files": len(results),
        "findings": sum(bool(x.get("suspicious_keywords")) for x in results),
        "results": results,
        "note": "Keyword matches require human review; they do not prove malicious activity.",
    }
    output = Path(args.output)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(f"Scanned {len(results)} files. Report: {output}")


if __name__ == "__main__":
    main()
'''

SIGNAL = r'''"""Tamanna defensive signal helpers; these functions do not block traffic."""


def detect_intrusion(event):
    text = str(event).lower()
    indicators = ("unauthorized", "failed_login", "strange_ip", "file_change")
    return any(indicator in text for indicator in indicators)


def tamanna_defense(event):
    if detect_intrusion(event):
        return "Tamanna: সতর্ক! সন্দেহজনক কার্যকলাপ ধরা পড়েছে."
    return "Tamanna: সব ঠিক আছে, সিস্টেম শান্ত."


if __name__ == "__main__":
    print(tamanna_defense("failed_login from unknown IP"))
'''

DEEP_POWER = r'''"""Tamanna state and synchronization helpers."""


class TamannaDeepPower:
    def __init__(self):
        self.state = "calm"
        self.energy = 1.0
        self.memory = []

    def log(self, event, detail):
        self.memory.append({"event": event, "detail": detail})

    def boost_energy(self, pressure):
        self.energy = round(self.energy + float(pressure) * 0.1, 2)
        self.log("energy_boost", self.energy)
        return self.energy

    def set_state(self, new_state):
        self.state = str(new_state)
        self.log("state_change", self.state)

    def heartbeat(self):
        self.log("heartbeat", self.state)

    def react(self, signal):
        mapping = {"ok": "calm", "warn": "alert", "error": "pain",
                   "recover": "healing"}
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
        self.log("heartbeat", (self.emotion, self.intel_state))

    def sync_emotion(self, signal):
        self.emotion = {
            "ok": "calm", "warn": "alert", "error": "pain", "deep": "focused"
        }.get(signal, "unknown")
        self.log("emotion_update", self.emotion)

    def sync_intelligence(self, signal):
        self.intel_state = {
            "ok": "stable", "warn": "monitoring",
            "error": "critical", "deep": "deep_mode"
        }.get(signal, "unknown")
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

    def sync(self, signal):
        self.emotion = {
            "ok": "calm", "warn": "alert", "error": "pain", "deep": "focused"
        }.get(signal, "unknown")
        self.intel = {
            "ok": "stable", "warn": "monitoring",
            "error": "critical", "deep": "deep_mode"
        }.get(signal, "unknown")
        self.sync_state = {
            "deep": "deep_sync", "error": "defense_sync"
        }.get(signal, "normal")
        self.log("sync", {
            "emotion": self.emotion, "intel": self.intel,
            "state": self.sync_state
        })


class TamannaPowerExpansion:
    def __init__(self):
        self.emotion = "calm"
        self.intel = "stable"
        self.sync = "normal"
        self.energy = 1.0

    def amplify(self):
        self.energy = round(self.energy * 1.2, 2)
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
        return {"emotion": self.emotion, "intel": self.intel,
                "sync": self.sync, "energy": self.energy}
'''

def backup(path):
    dest = BACKUP / path.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Apply replacements after creating backups")
    args = parser.parse_args()

    if not (ROOT / ".git").exists():
        print("ERROR: Run from the root of the cloned Git repository.")
        return 2

    replacements = {
        "runner/python/radar.py": RADAR,
        "runner/python/signal.py": SIGNAL,
        "runner/python/tamanna_deep_power.py": DEEP_POWER,
    }
    results = []
    for relative, content in replacements.items():
        path = ROOT / relative
        if not path.exists():
            results.append({"file": relative, "status": "missing"})
            continue
        old = path.read_text(encoding="utf-8")
        new = content.rstrip() + "\n"
        if old == new:
            results.append({"file": relative, "status": "already_fixed"})
            continue
        results.append({"file": relative,
                        "status": "replaced" if args.apply else "would_replace"})
        if args.apply:
            backup(path)
            path.write_text(new, encoding="utf-8")

    # TamannaAI is deliberately not overwritten; preserve its original features.
    ai_path = ROOT / "runner/python/tamanna_ai.py"
    if ai_path.exists():
        results.append({
            "file": "runner/python/tamanna_ai.py",
            "status": "needs_separate_review_preserved"
        })

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry-run",
        "backup": str(BACKUP) if args.apply else None,
        "results": results,
    }
    report_path = ROOT / "tamanna_remaining_fix_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    for item in results:
        print(item["status"] + ": " + item["file"])
    print("Report:", report_path)
    if not args.apply:
        print("No source files changed. Review, then rerun with --apply.")
    else:
        print("Backups:", BACKUP)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY

python3 -m py_compile scripts/tamanna_remaining_fix.py
python3 scripts/tamanna_remaining_fix.py
