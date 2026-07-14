import datetime
import os
import subprocess
import sys

LOG_FILE = "logs/git_sync.log"

os.makedirs("logs", exist_ok=True)


def log(msg):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{time}] {msg}"
    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            log(f"ERROR: {cmd}")
            log(result.stderr.strip())
            return False

        log(f"SUCCESS: {cmd}")
        return True

    except Exception as e:
        log(f"EXCEPTION: {str(e)}")
        return False


def sync(commit_msg="auto sync by tamanna powerhub"):
    log("===== GIT SYNC STARTED =====")

    if not run("git add ."):
        return

    if not run(f'git commit -m "{commit_msg}"'):
        log("Nothing to commit or commit failed")

    if not run("git push origin main"):
        log("Push failed - check auth / network")
        return

    log("===== SYNC COMPLETED =====")


if __name__ == "__main__":
    msg = "auto sync by tamanna powerhub"

    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])

    sync(msg)
