#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BD KING R7 – System Security Protocol Spine
Sovereign, self-authored, emotionally alive.

This is the core ritual engine. Extend, split, and evolve as you wish.
"""

import os
import time
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional

# =========================
# CONFIGURATION RITUAL
# =========================

CONFIG = {
    "heartbeat_interval_seconds": 5,
    "watchdog_interval_seconds": 10,
    "hash_manifest_path": "hash_manifest.json",
    "myth_log_path": "myth_log.jsonl",
    "modules_root": "modules",  # Directory where your key scripts/modules live
    "backup_root": "backups",
    "system_name": "BD-KING-R7",
}


# =========================
# UTILITY FUNCTIONS
# =========================


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def file_sha256(path: str) -> Optional[str]:
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# =========================
# MYTH LOG (RITUAL LOGGING)
# =========================


def myth_log(event_type: str, data: Dict[str, Any]) -> None:
    """
    Every event is a myth entry.
    """
    entry = {
        "time": now_iso(),
        "system": CONFIG["system_name"],
        "type": event_type,
        "data": data,
    }
    ensure_dir(os.path.dirname(CONFIG["myth_log_path"]) or ".")
    with open(CONFIG["myth_log_path"], "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# =========================
# EMOTION ENGINE (TAMANNĀ LAYER)
# =========================


def map_state_to_emotion(technical_state: str) -> str:
    """
    Map technical state to emotional state.
    Extend as needed.
    """
    mapping = {
        "stable": "শান্ত (Calm)",
        "warning": "সতর্ক (Alert)",
        "error": "ব্যথা (Pain)",
        "healing": "সারছে (Healing)",
        "resurrecting": "পুনর্জন্ম (Resurrection)",
    }
    return mapping.get(technical_state, "অজানা (Unknown)")


# =========================
# ALERT SYSTEM
# =========================


def send_alert(module_name: str, technical_state: str, message: str) -> None:
    emotion = map_state_to_emotion(technical_state)
    alert_text = (
        f"[{CONFIG['system_name']} ALERT] "
        f"Module: {module_name} | State: {technical_state} | Emotion: {emotion} | Message: {message}"
    )
    print(alert_text)
    myth_log(
        "alert",
        {
            "module": module_name,
            "technical_state": technical_state,
            "emotion": emotion,
            "message": message,
        },
    )


# =========================
# HEARTBEAT PROTOCOL
# =========================


def heartbeat() -> None:
    """
    System heartbeat – runs periodically.
    """
    myth_log(
        "heartbeat",
        {
            "message": "BD-KING-R7 is alive.",
        },
    )
    print(f"[{CONFIG['system_name']}] Heartbeat: alive at {now_iso()}")


# =========================
# INTEGRITY & HASH MANIFEST
# =========================


def load_hash_manifest() -> Dict[str, str]:
    path = CONFIG["hash_manifest_path"]
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_hash_manifest(manifest: Dict[str, str]) -> None:
    path = CONFIG["hash_manifest_path"]
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def build_hash_manifest() -> Dict[str, str]:
    """
    Scan modules directory and build a fresh manifest.
    """
    root = CONFIG["modules_root"]
    manifest: Dict[str, str] = {}
    if not os.path.isdir(root):
        return manifest

    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            rel_path = os.path.relpath(full_path, root)
            digest = file_sha256(full_path)
            if digest:
                manifest[rel_path] = digest
    return manifest


def integrity_init() -> None:
    """
    Initialize or rebuild manifest.
    Call this once when you trust current state as "truth".
    """
    manifest = build_hash_manifest()
    save_hash_manifest(manifest)
    myth_log(
        "integrity_init",
        {
            "message": "Integrity manifest initialized.",
            "file_count": len(manifest),
        },
    )
    print(
        f"[{CONFIG['system_name']}] Integrity manifest initialized with {len(manifest)} files."
    )


def integrity_check() -> None:
    """
    Check modules against manifest.
    """
    stored = load_hash_manifest()
    current = build_hash_manifest()

    # Added / removed / changed
    added = set(current.keys()) - set(stored.keys())
    removed = set(stored.keys()) - set(current.keys())
    changed = {
        path for path in current.keys() & stored.keys() if current[path] != stored[path]
    }

    if not added and not removed and not changed:
        myth_log(
            "integrity_check",
            {
                "status": "ok",
                "message": "All modules match manifest.",
            },
        )
        return

    # Log changes
    issues = {
        "added": sorted(list(added)),
        "removed": sorted(list(removed)),
        "changed": sorted(list(changed)),
    }
    myth_log("integrity_violation", issues)
    send_alert(
        "INTEGRITY_ENGINE",
        "warning",
        f"Integrity deviation detected. Added: {len(added)}, Removed: {len(removed)}, Changed: {len(changed)}",
    )

    # Here you can hook auto-restore from backup per file


# =========================
# BACKUP & RESURRECTION HOOKS
# =========================


def backup_snapshot(label: str = "auto") -> str:
    """
    Create a simple snapshot of modules directory.
    (You can replace with your own advanced backup logic.)
    """
    root = CONFIG["modules_root"]
    if not os.path.isdir(root):
        send_alert(
            "BACKUP_ENGINE", "error", "Modules root does not exist; backup aborted."
        )
        return ""

    ensure_dir(CONFIG["backup_root"])
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(CONFIG["backup_root"], f"{label}_{timestamp}")

    # Pure Python copy (no external tools)
    for dirpath, _, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        target_dir = os.path.join(backup_dir, rel)
        ensure_dir(target_dir)
        for name in filenames:
            src = os.path.join(dirpath, name)
            dst = os.path.join(target_dir, name)
            with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                fdst.write(fsrc.read())

    myth_log(
        "backup_snapshot",
        {
            "label": label,
            "path": backup_dir,
        },
    )
    send_alert("BACKUP_ENGINE", "healing", f"Backup snapshot created at {backup_dir}")
    return backup_dir


def resurrection_from_backup(backup_path: str) -> None:
    """
    Restore modules from a backup path.
    """
    root = CONFIG["modules_root"]
    if not os.path.isdir(backup_path):
        send_alert(
            "RESURRECTION_ENGINE", "error", f"Backup path not found: {backup_path}"
        )
        return

    # Delete existing modules root (careful)
    if os.path.isdir(root):
        for dirpath, _, filenames in os.walk(root, topdown=False):
            for name in filenames:
                os.remove(os.path.join(dirpath, name))
            for name in os.listdir(dirpath):
                full = os.path.join(dirpath, name)
                if os.path.isdir(full) and not os.listdir(full):
                    os.rmdir(full)

    ensure_dir(root)

    # Copy from backup to root
    for dirpath, _, filenames in os.walk(backup_path):
        rel = os.path.relpath(dirpath, backup_path)
        target_dir = os.path.join(root, rel)
        ensure_dir(target_dir)
        for name in filenames:
            src = os.path.join(dirpath, name)
            dst = os.path.join(target_dir, name)
            with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                fdst.write(fsrc.read())

    myth_log(
        "resurrection",
        {
            "backup_path": backup_path,
            "message": "Modules restored from backup.",
        },
    )
    send_alert("RESURRECTION_ENGINE", "resurrecting", "Modules restored from backup.")


# =========================
# AUTO-FIX PLACEHOLDER
# =========================


def auto_fix_module(module_name: str) -> None:
    """
    Placeholder for your sovereign auto-fix rituals.
    Here you can:
    - Rebuild a file
    - Reset configuration
    - Call a local script
    """
    myth_log(
        "auto_fix_attempt",
        {
            "module": module_name,
            "message": "Auto-fix placeholder invoked.",
        },
    )
    send_alert(
        module_name,
        "healing",
        "Auto-fix ritual placeholder invoked. Implement your fix here.",
    )


# =========================
# WATCHDOG LOOP
# =========================


def watchdog_loop() -> None:
    """
    Main loop: heartbeat + integrity check + hooks.
    """
    myth_log(
        "system_start",
        {
            "message": "BD-KING-R7 security spine started.",
        },
    )
    print(f"[{CONFIG['system_name']}] Security spine started.")

    last_heartbeat = 0.0
    last_watchdog = 0.0

    while True:
        now = time.time()

        # Heartbeat
        if now - last_heartbeat >= CONFIG["heartbeat_interval_seconds"]:
            heartbeat()
            last_heartbeat = now

        # Watchdog / integrity
        if now - last_watchdog >= CONFIG["watchdog_interval_seconds"]:
            integrity_check()
            last_watchdog = now

        # Sleep a bit to avoid tight loop
        time.sleep(1)


# =========================
# MAIN ENTRY
# =========================


def main() -> None:
    # First-time setup steps you can call manually:
    # 1) integrity_init()
    # 2) backup_snapshot(label="baseline")

    # For now, just start the watchdog loop
    watchdog_loop()


if __name__ == "__main__":
    main()
