#!/usr/bin/env python3
"""
Simple long-running worker.
Replace `do_work()` with your real logic.
Logs to /var/log/myauto.log
"""

import json
import logging
import signal
import time
import traceback
from pathlib import Path

LOGFILE = "/var/log/myauto.log"
CONFIG_FILE = Path("/etc/myauto/config.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOGFILE), logging.StreamHandler()],
)

stop_requested = False


def handle_sigterm(signum, frame):
    global stop_requested
    logging.info("Stop requested (signal %s).", signum)
    stop_requested = True


signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)


def load_config():
    if not CONFIG_FILE.exists():
        logging.warning(
            "Config file %s not found. Using defaults.", CONFIG_FILE)
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        logging.exception("Failed to load config.")
        return {}


def do_work(cfg):
    """
    Put the real task here. This example just logs timestamp.
    Replace with: calling APIs, processing queue, file operations, etc.
    """
    # Example: check a folder for tasks
    logging.info("Worker heartbeat. cfg keys: %s", list(cfg.keys()))
    # simulate work
    time.sleep(2)


def main():
    logging.info("Starting myauto worker.")
    cfg = load_config()
    try:
        while not stop_requested:
            try:
                do_work(cfg)
            except Exception:
                logging.error("Error during work: %s", traceback.format_exc())
                # if desired, wait a bit on error
                time.sleep(5)
        logging.info("Worker stopping cleanly.")
    except Exception:
        logging.exception("Unhandled exception in main.")
    finally:
        logging.info("Exiting.")


if __name__ == "__main__":
    main()
