import os
import subprocess
import time

GIT_REPO_DIR = os.path.expanduser("~/bd-king-r7-system")
TAMANNA_APP_DIR = os.path.join(GIT_REPO_DIR, "tamanna-android")
JAVA_HOME = "/path/to/jdk17"
SYNC_INTERVAL = 300

def run_command(cmd, cwd=None):
    print(f"[RUN] {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    print(f"[RETURN CODE] {result.returncode}")
    return result.returncode

def build_tamanna_apk():
    gradlew = "gradlew.bat" if os.name == "nt" else "./gradlew"
    os.environ["JAVA_HOME"] = JAVA_HOME
    run_command(f"{gradlew} assembleDebug", cwd=TAMANNA_APP_DIR)

def git_pull_push():
    run_command("git pull origin main", cwd=GIT_REPO_DIR)
    run_command("git add .", cwd=GIT_REPO_DIR)
    commit_message = f"Auto sync {time.strftime('%Y-%m-%d %H:%M:%S')}"
    run_command(f'git commit -m "{commit_message}"', cwd=GIT_REPO_DIR)
    run_command("git push origin main", cwd=GIT_REPO_DIR)

if __name__ == "__main__":
    print("=== Tamanna Auto Build & Sync ===")
    while True:
        try:
            git_pull_push()
            build_tamanna_apk()
            print(f"Waiting {SYNC_INTERVAL} seconds...")
            time.sleep(SYNC_INTERVAL)
        except KeyboardInterrupt:
            print("Stopped by user")
            break
# main.py
def system_status():
    return "BD-KING-R7 Program Active"