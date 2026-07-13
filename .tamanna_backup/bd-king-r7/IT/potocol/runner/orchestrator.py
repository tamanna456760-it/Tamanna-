import time
import subprocess

def run(cmd):
    print(f"[RUN] {cmd}")
    subprocess.call(cmd, shell=True)

def main_loop():
    while True:
        print("=== TAMANNA POWERHUB ORCHESTRATOR ===")

        # 1. scan issues
        run("python3 automation/lint_and_detect_issues.py")

        # 2. auto fix
        run("python3 automation/auto_fix_issues.py")

        # 3. security monitor
        run("python3 security/security_logger.py")

        # 4. brain update
        run("python3 core/ai_brain_core.py")

        # 5. sync to github
        run("python3 sync/git_sync.py")

        time.sleep(10)

if __name__ == "__main__":
    main_loop()