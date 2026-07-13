import json
import subprocess
import time


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
    watch_and_sync
    import json
    import subprocess
    import time


def load_config():
    with open("config.json") as f:
        return json.load(f)


def sync_repo(repo, msg):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[SYNC] Completed")
    except Exception as e:
        print(f"[SYNC ERROR] {e}")


def main():
    cfg = load_config()
    while True:
        sync_repo(cfg["git_repo"], cfg["auto_commit_message"])
        time.sleep(cfg["scan_interval_sec"])


if __name__ == "__main__":
    main()
