#!/usr/bin/env python3
"""
Entry point for Earth BD-KING-R7 PowerHub Master.
Run the API + Sync server and expose web UI.
"""

import os
from threading import Thread

from powerhub.builder import build_all
from powerhub.core import PowerHubController
from powerhub.installer import install_system
from powerhub.sync_server import run_sync_server


def main():
    # Ensure logs dir exists
    os.makedirs("logs", exist_ok=True)

    # Start powerhub controller (in-memory)
    controller = PowerHubController()

    # Start Flask sync server in a thread
    api_thread = Thread(target=run_sync_server, args=(controller,), daemon=True)
    api_thread.start()
    print("[MANAGE] Sync server started in background")

    # Optional: run installer/build steps once
    install_system()
    build_all()

    print("[MANAGE] BD-KING-R7 PowerHub Master running.")
    print("Open http://127.0.0.1:5000 in your browser to control modules.")
    api_thread.join()


if __name__ == "__main__":
    main()
