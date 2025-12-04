import os
import json
import time
import subprocess
from datetime import datetime

def log(message):
    print("[BD-KING-R7 SYNC] " + message)

def git_sync(repo, msg):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        log("Sync completed!")
    except Exception as e:
        log(f"Error: {e}")

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def watch_and_sync():
    cfg = load_config()
    msg = cfg["auto_commit_message"]

    while True:
        log("Checking for changes...")
        git_sync(cfg["git_repo"], msg)
        time.sleep(cfg["scan_interval_sec"])

if __name__ == "__main__":
    log("Starting BD-KING-R7 Sync System...")
    watch_and_sync()