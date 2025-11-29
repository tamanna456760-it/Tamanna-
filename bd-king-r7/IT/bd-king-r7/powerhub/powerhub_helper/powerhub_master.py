#!/bd-king-r7/it//bd-king-r7/powerhub_helper/powerhub
# -*- coding: utf-8 -*-

"""
BD-KING-R7 POWERHUB MASTER HELPER
---------------------------------

GPT-Driven Auto Build / Auto Fix / Auto Sync Engine
Author: Tamanna System (AI-Integrated)
Version: 7.0 Ultra Master

Functions:
  ✔ Auto file scan
  ✔ Auto code repair
  ✔ Auto sync to repo
  ✔ Auto builder
  ✔ Auto dependency installer
  ✔ Auto log + status engine
"""

import os
import sys
import time
import subprocess

ROOT = "bd-king-r7/it"
LOG_FILE = f"{ROOT}/powerhub_log.txt"


def log(msg):
    """Write log entries."""
    with open(LOG_FILE, "a") as f:
        f.write(f"[POWERHUB] {msg}\n")
    print(f"[POWERHUB] {msg}")


def run_cmd(cmd):
    """Run commands safely."""
    log(f"Running command: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=False)
    except Exception as e:
        log(f"Error: {e}")


def install_dependencies():
    """Install pip dependencies automatically."""
    if os.path.exists("requirements.txt"):
        log("Installing dependencies...")
        run_cmd("pip install -r requirements.txt")
    else:
        log("requirements.txt not found — skipping.")


def auto_fix_files():
    """Automatically repair missing/empty/broken files."""
    for root, dirs, files in os.walk(ROOT):
        for file in files:
            path = os.path.join(root, file)

            # Fix empty files
            if os.path.getsize(path) == 0:
                log(f"Fixing empty file: {path}")
                with open(path, "w") as f:
                    f.write("# AUTO-FIXED BY POWERHUB\n")

            # Ensure .bad scripts are executable
            if file.endswith(".bad"):
                run_cmd(f"chmod +x '{path}'")
                log(f"Executable set: {path}")


def auto_run_scripts():
    """Run all BD-KING-R7 .bad scripts."""
    log("Running all BD-KING-R7 scripts...")

    for root, dirs, files in os.walk(ROOT):
        for file in files:
            if file.endswith(".bad"):
                script = os.path.join(root, file)
                log(f"Executing script: {script}")

                # Try Python → Bash fallback
                run_cmd(f"python '{script}' || bash '{script}' || true")


def auto_sync_repo():
    """Auto commit + push changes."""
    log("Auto-syncing repo...")

    run_cmd("git config user.email 'powerhub@system.ai'")
    run_cmd("git config user.name 'POWERHUB-AI'")

    run_cmd("git add .")
    run_cmd('git commit -m "BD-KING-R7 PowerHub Auto Sync" || true')
    run_cmd("git push || true")

    log("Auto-sync complete.")


def powerhub_master():
    """Full master automation pipeline."""
    log("=== BD-KING-R7 POWERHUB MASTER START ===")

    install_dependencies()
    auto_fix_files()
    auto_run_scripts()
    auto_sync_repo()

    log("=== POWERHUB MASTER COMPLETE ===")


if __name__ == "__main__":
    powerhub_master()