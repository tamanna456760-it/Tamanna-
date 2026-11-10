#!/usr/bin/env python3
"""Daily sync scheduler; executes only an existing local script without a shell."""
import logging
import subprocess
import sys
import time
from pathlib import Path

import schedule

LOG = logging.getLogger("tamanna_auto_sync")
LOG.setLevel(logging.INFO)
if not LOG.handlers:
    LOG.addHandler(logging.StreamHandler(sys.stdout))
SCRIPT_DIR = Path(__file__).resolve().parent


def run_sync_script(script_name):
    script = (SCRIPT_DIR / script_name).resolve()
    if script.parent != SCRIPT_DIR or not script.is_file():
        LOG.error("Sync script is missing or outside the runner directory: %s", script_name)
        return False
    try:
        subprocess.run(
            [sys.executable, str(script)],
            cwd=str(SCRIPT_DIR),
            check=True,
            timeout=900,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        LOG.exception("Scheduled sync script failed: %s", script_name)
        return False


def job():
    run_sync_script("tamanna_book_sync.py")


schedule.every().day.at("03:00").do(job)

if __name__ == "__main__":
    LOG.info("Tamanna AI Auto Sync scheduler started")
    while True:
        schedule.run_pending()
        time.sleep(30)
