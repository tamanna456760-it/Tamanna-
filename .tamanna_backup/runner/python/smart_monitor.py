import os
import time
import shutil
from datetime import datetime

WATCH_PATH = "."
LOG_FILE = "smart_monitor.log"
SCAN_INTERVAL = 5

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "runner"
}

IGNORE_FILES = {
    LOG_FILE,
    "smart_monitor.py"
}

FOLDERS = {
    "python": "runner/python",
    "node": "runner/node",
    "shell": "runner/shell",
    "html": "runner/web",
    "json": "runner/data"
}


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)


def ensure_dirs():
    for p in FOLDERS.values():
        os.makedirs(p, exist_ok=True)


def detect_type(file):
    if file.endswith(".py"):
        return "python"
    if file.endswith(".js"):
        return "node"
    if file.endswith(".sh"):
        return "shell"
    if file.endswith(".html"):
        return "html"
    if file.endswith(".json"):
        return "json"
    return None


def should_ignore(path):
    for f in IGNORE_FILES:
        if path.endswith(f):
            return True

    for d in IGNORE_DIRS:
        if f"/{d}/" in path:
            return True

    return False


def already_routed(path):
    return "/runner/" in path


def move_file(path, ftype):
    if ftype not in FOLDERS:
        return

    dest = os.path.join(FOLDERS[ftype], os.path.basename(path))

    if os.path.exists(dest):
        return

    try:
        shutil.move(path, dest)
        log(f"📦 Moved: {path} -> {dest}")
    except Exception as e:
        log(f"❌ Move error: {e}")


def scan():
    for root, dirs, files in os.walk(WATCH_PATH):
        if "runner" in root:
            continue

        for file in files:
            path = os.path.join(root, file)

            if should_ignore(path):
                continue

            if already_routed(path):
                continue

            ftype = detect_type(path)

            if ftype:
                move_file(path, ftype)


def run():
    ensure_dirs()
    log("🚀 Smart Monitor Running (Stable)")

    while True:
        scan()
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Stopped")
