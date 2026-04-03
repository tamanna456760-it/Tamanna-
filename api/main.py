import json
import requests
import subprocess
import time
import logging

# Load configuration
with open("config.json") as f:
    config = json.load(f)

# Setup logging
logging.basicConfig(
    filename=config["logging"]["log_file"],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Tamanna System Launcher Started")

# Heartbeat function
def heartbeat():
    try:
        response = requests.get(
            f"{config['api']['endpoint']}/heartbeat",
            headers={"Authorization": f"Bearer {config['api']['auth_token']}"},
            timeout=config['api']['timeout']
        )
        if response.status_code == 200:
            logging.info("Heartbeat OK")
        else:
            logging.warning(f"Heartbeat Failed: {response.status_code}")
    except Exception as e:
        logging.error(f"Heartbeat Exception: {e}")

# Run auto sync
def auto_sync():
    try:
        subprocess.run(["bash", config["sync"]["script"]], check=True)
        logging.info("Auto Sync Completed")
    except subprocess.CalledProcessError as e:
        logging.error(f"Auto Sync Failed: {e}")

# Main loop
SYNC_INTERVAL = config["sync"]["interval_minutes"] * 60

while True:
    heartbeat()
    auto_sync()
    time.sleep(SYNC_INTERVAL)