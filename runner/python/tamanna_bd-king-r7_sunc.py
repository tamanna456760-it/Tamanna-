#!/usr/bin/env python3
"""Conservative local mirror sync; destructive deletes and build commands are opt-in."""
import hashlib
import json
import os
import shlex
import subprocess
import time
from datetime import datetime
from pathlib import Path

BD_KING_ROOT = Path(__file__).resolve().parent.parent
WATCH_PATHS = [
    BD_KING_ROOT / "code",
    BD_KING_ROOT / "engines",
    BD_KING_ROOT / "build",
    BD_KING_ROOT / "panels",
]
SYNC_ROOT = BD_KING_ROOT / "sync_root" / "mirror_all"
LOG_DIR = BD_KING_ROOT / "logs"
LOG_FILE = LOG_DIR / "tamanna_sync.log"
STATE_FILE = LOG_DIR / "tamanna_sync_state.json"
SCAN_INTERVAL = 30
# Commands must be configured as argument arrays, never shell command strings.
BUILD_COMMANDS = []
ALLOW_MIRROR_DELETE = os.environ.get("TAMANNA_ALLOW_MIRROR_DELETE") == "1"
ALLOW_BUILD_COMMANDS = os.environ.get("TAMANNA_ALLOW_BUILD_COMMANDS") == "1"

SECRET_NAMES = {
    ".env", ".env.local", ".env.production", "credentials.json",
    "token.json", "token.pickle", "id_rsa", "id_ed25519",
    "service-account.json", "secrets.json",
}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


def is_safe_file(path):
    if path.is_symlink() or not path.is_file():
        return False
    parts = [part.lower() for part in path.parts]
    if any(part in SECRET_NAMES or part.startswith(".env.") for part in parts):
        return False
    if path.suffix.lower() in SECRET_SUFFIXES:
        return False
    return True


def log(message):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().isoformat(timespec='seconds')}] TamannaSync :: {message}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def hash_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_all_files():
    state = {}
    for base in WATCH_PATHS:
        if not base.is_dir():
            continue
        for root, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = [name for name in dirs if not (Path(root) / name).is_symlink()]
            for name in files:
                full_path = Path(root) / name
                if not is_safe_file(full_path):
                    continue
                rel_path = full_path.relative_to(BD_KING_ROOT).as_posix()
                try:
                    state[rel_path] = hash_file(full_path)
                except OSError as error:
                    log(f"WARNING: Could not hash {rel_path}: {error}")
    return state


def load_previous_state():
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError) as error:
        log(f"WARNING: Could not load state: {error}")
        return {}


def save_state(state):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temporary.replace(STATE_FILE)


def diff_states(old, new):
    old_keys, new_keys = set(old), set(new)
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = sorted(key for key in old_keys & new_keys if old[key] != new[key])
    return added, changed, removed


def contained_path(root, relative):
    candidate = (root / relative).resolve()
    if root.resolve() not in candidate.parents:
        raise ValueError(f"Path escapes mirror root: {relative}")
    return candidate


def sync_file(rel_path):
    source = contained_path(BD_KING_ROOT, rel_path)
    if not is_safe_file(source):
        log(f"SKIP unsafe source :: {rel_path}")
        return
    destination = contained_path(SYNC_ROOT, rel_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())
    log(f"SYNC UPDATE :: {rel_path}")


def remove_synced_file(rel_path):
    if not ALLOW_MIRROR_DELETE:
        log(f"DELETE SKIPPED (TAMANNA_ALLOW_MIRROR_DELETE not set) :: {rel_path}")
        return
    destination = contained_path(SYNC_ROOT, rel_path)
    if destination.is_file() and not destination.is_symlink():
        destination.unlink()
        log(f"SYNC REMOVE :: {rel_path}")


def run_build_commands():
    if not ALLOW_BUILD_COMMANDS or not BUILD_COMMANDS:
        log("BUILD skipped; explicit opt-in and argument-list commands are required")
        return
    for command in BUILD_COMMANDS:
        if not isinstance(command, (list, tuple)) or not command:
            raise ValueError("BUILD_COMMANDS entries must be non-empty argument lists")
        if any(token in {";", "&&", "||", "|", ">", ">>", "<"} for token in command):
            raise ValueError("Shell operators are not permitted in build commands")
        log(f"BUILD CMD :: {command[0]}")
        result = subprocess.run(
            [str(part) for part in command],
            cwd=str(BD_KING_ROOT),
            check=False,
            timeout=900,
        )
        if result.returncode:
            raise RuntimeError(f"Build command failed with exit code {result.returncode}")


def main_loop():
    log("Tamanna Sync Engine started in conservative mode")
    SYNC_ROOT.mkdir(parents=True, exist_ok=True)
    previous = load_previous_state()
    while True:
        try:
            current = scan_all_files()
            added, changed, removed = diff_states(previous, current)
            for relative in added + changed:
                sync_file(relative)
            for relative in removed:
                remove_synced_file(relative)
            if added or changed or removed:
                save_state(current)
                run_build_commands()
                log(f"Cycle complete: added={len(added)}, changed={len(changed)}, removed={len(removed)}")
            else:
                log("No changes detected")
            previous = current
            time.sleep(SCAN_INTERVAL)
        except KeyboardInterrupt:
            log("Sync engine stopped")
            return
        except Exception as error:
            log(f"ERROR: {error}")
            time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main_loop()
