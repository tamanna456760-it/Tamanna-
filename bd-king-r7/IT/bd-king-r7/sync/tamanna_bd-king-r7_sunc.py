#!/usr/bin/env python3
import os
import time
import hashlib
import json
import shutil
from datetime import datetime

# ================= CONFIG: EDIT FOR YOUR SYSTEM =================

# Root of BD KING R7
BD_KING_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Where to scan for code and power modules
WATCH_PATHS = [
    os.path.join(BD_KING_ROOT, "code"),
    os.path.join(BD_KING_ROOT, "engines"),
    os.path.join(BD_KING_ROOT, "build"),
    os.path.join(BD_KING_ROOT, "panels")  # if you have this
]

# Where to sync (central mirror)
SYNC_ROOT = os.path.join(BD_KING_ROOT, "sync_root", "mirror_all")

# Log + state files
LOG_DIR = os.path.join(BD_KING_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "tamanna_sync.log")
STATE_FILE = os.path.join(LOG_DIR, "tamanna_sync_state.json")

# How often to check (seconds)
SCAN_INTERVAL = 10

# Build commands to run after successful sync (edit as you like)
BUILD_COMMANDS = [
    # Example: "bash build/build_all.sh",
    # Example: "python3 build/build_all.py"
]

# ================== UTILITY FUNCTIONS ===========================

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] TamannaSync :: {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def hash_file(path):
    """Return hash of a file, or None if cannot read."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        log(f"WARNING: Could not hash {path}: {e}")
        return None


def scan_all_files():
    """Scan watched paths and return dict: {relative_path: hash}."""
    state = {}
    for base in WATCH_PATHS:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for name in files:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, BD_KING_ROOT)
                file_hash = hash_file(full_path)
                if file_hash:
                    state[rel_path] = file_hash
    return state


def load_previous_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"WARNING: Could not load state file: {e}")
        return {}


def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"WARNING: Could not save state file: {e}")


def diff_states(old, new):
    """Compare two states, return added, changed, removed lists of relative paths."""
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    added = sorted(list(new_keys - old_keys))
    removed = sorted(list(old_keys - new_keys))

    changed = []
    for path in (old_keys & new_keys):
        if old[path] != new[path]:
            changed.append(path)
    changed.sort()

    return added, changed, removed


def ensure_dir_for_file(full_path):
    os.makedirs(os.path.dirname(full_path), exist_ok=True)


def sync_file(rel_path):
    src = os.path.join(BD_KING_ROOT, rel_path)
    dest = os.path.join(SYNC_ROOT, rel_path)

    if not os.path.exists(src):
        # If source is gone, we may want to delete from sync mirror
        if os.path.exists(dest):
            os.remove(dest)
            log(f"SYNC REMOVE :: {rel_path}")
        return

    ensure_dir_for_file(dest)
    shutil.copy2(src, dest)
    log(f"SYNC UPDATE :: {rel_path}")


def remove_synced_file(rel_path):
    dest = os.path.join(SYNC_ROOT, rel_path)
    if os.path.exists(dest):
        os.remove(dest)
        log(f"SYNC REMOVE :: {rel_path}")


def run_build_commands():
    if not BUILD_COMMANDS:
        log("BUILD :: No BUILD_COMMANDS configured, skipping.")
        return

    log("BUILD :: Starting build sequence...")
    for cmd in BUILD_COMMANDS:
        log(f"BUILD CMD :: {cmd}")
        # Safe: using os.system. You can replace with subprocess if you want more control.
        exit_code = os.system(cmd)
        if exit_code == 0:
            log(f"BUILD OK :: {cmd}")
        else:
            log(f"BUILD FAIL ({exit_code}) :: {cmd}")
    log("BUILD :: Completed build sequence.")


# ================== MAIN LOOP ==================================

def main_loop():
    log("Tamanna Sync Engine for BD KING R7 :: START")
    os.makedirs(SYNC_ROOT, exist_ok=True)

    prev_state = load_previous_state()

    while True:
        try:
            current_state = scan_all_files()
            added, changed, removed = diff_states(prev_state, current_state)

            if added or changed or removed:
                log("CHANGE DETECTED :: Sync and build ritual begins.")
                if added:
                    log(f"ADDED   :: {len(added)} file(s)")
                if changed:
                    log(f"CHANGED :: {len(changed)} file(s)")
                if removed:
                    log(f"REMOVED :: {len(removed)} file(s)")

                # Sync added and changed
                for rel in added + changed:
                    sync_file(rel)

                # Remove deleted from sync mirror
                for rel in removed:
                    remove_synced_file(rel)

                # Save new state
                save_state(current_state)

                # Run build ritual
                run_build_commands()
            else:
                log("NO CHANGE :: Heartbeat only.")

            prev_state = current_state
            time.sleep(SCAN_INTERVAL)

        except KeyboardInterrupt:
            log("Tamanna Sync Engine :: STOP (KeyboardInterrupt)")
            break

        except Exception as e:
            log(f"ERROR in main loop: {e}")
            time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main_loop()
