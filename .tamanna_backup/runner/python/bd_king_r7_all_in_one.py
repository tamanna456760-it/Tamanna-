import os
import json
import time
import shutil
from datetime import datetime

# ======================
# SYSTEM CONFIG
# ======================
SYSTEM_NAME = "BD-KING-R7"
MANIFEST = "manifest.json"
LOG_FILE = "system_log.jsonl"
BACKUP_DIR = "backup"


# ======================
# LOGGER MODULE
# ======================
def log(event, level="info", data=None):
    entry = {
        "time": datetime.utcnow().isoformat() + "Z",
        "system": SYSTEM_NAME,
        "level": level,
        "event": event,
    }
    if data:
        entry.update(data)

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ======================
# CORE MODULE
# ======================
def load_manifest():
    if os.path.exists(MANIFEST):
        with open(MANIFEST, "r") as f:
            log("manifest_loaded")
            return json.load(f)
    log("manifest_missing", level="error")
    return {}


# ======================
# SYNC MODULE
# ======================
def auto_sync(interval=10):
    files = sum(len(files) for _, _, files in os.walk("."))
    log("auto_sync_check", data={"files_checked": files})
    time.sleep(interval)


# ======================
# HEARTBEAT MODULE
# ======================
def heartbeat():
    log("system_heartbeat", data={"status": "alive"})


# ======================
# BACKUP MODULE
# ======================
def backup_system():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = int(time.time())
    name = f"{BACKUP_DIR}/backup_{ts}"
    shutil.make_archive(name, "zip", ".")
    log("backup_created", data={"file": name})


# ======================
# PERFORMANCE MODULE
# ======================
def performance_check():
    start = time.time()
    time.sleep(0.05)
    duration = round(time.time() - start, 4)
    log("performance_check", data={"response_time": duration})


# ======================
# INTERFACE MODULE
# ======================
def command(cmd):
    log("command_received", data={"command": cmd})
    return f"Executed: {cmd}"


# ======================
# MAIN SYSTEM LOOP
# ======================
if __name__ == "__main__":
    log("system_init", data={"status": "ready"})
    log("system_start")

    load_manifest()

    while True:
        auto_sync()
        heartbeat()
        performance_check()
