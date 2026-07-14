import os
import time
import shutil
import subprocess
from datetime import datetime

WATCH_PATH = "."
REPO_PATH = "."
SCAN_INTERVAL = 10

LOG_FILE = "auto_sync.log"

IGNORE_DIRS = {".git", "__pycache__", "node_modules", "runner"}

FOLDERS = {
    "python": "runner/python",
    "node": "runner/node",
    "shell": "runner/shell",
    "html": "runner/web",
    "json": "runner/data",
}


# ---------------- LOG ----------------
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)


# ---------------- TYPE DETECT ----------------
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


# ---------------- MOVE ----------------
def move_file(path, ftype):
    if ftype not in FOLDERS:
        return

    dest_folder = FOLDERS[ftype]
    os.makedirs(dest_folder, exist_ok=True)

    dest = os.path.join(dest_folder, os.path.basename(path))

    if os.path.exists(dest):
        return

    try:
        shutil.move(path, dest)
        log(f"📦 Moved: {path} -> {dest}")
    except Exception as e:
        log(f"Move error: {e}")


# ---------------- GIT AUTO SYNC ----------------
def git_sync():
    try:
        subprocess.run(["git", "add", "."], check=True)

        commit_msg = f"auto sync {datetime.now()}"

        subprocess.run(["git", "commit", "-m", commit_msg], check=False)

        subprocess.run(["git", "push"], check=False)

        log("🚀 GitHub synced successfully")

    except Exception as e:
        log(f"Git error: {e}")


# ---------------- SCAN ----------------
def scan():
    for root, dirs, files in os.walk(WATCH_PATH):

        if any(x in root for x in IGNORE_DIRS):
            continue

        for file in files:
            path = os.path.join(root, file)

            if "/runner/" in path:
                continue

            ftype = detect_type(path)

            if ftype:
                move_file(path, ftype)


# ---------------- MAIN LOOP ----------------
def run():
    log("🚀 Auto Sync Monitor Started")

    while True:
        scan()
        git_sync()
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    run()
