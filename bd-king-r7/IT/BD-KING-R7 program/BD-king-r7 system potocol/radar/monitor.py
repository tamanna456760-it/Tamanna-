import os
import time
import json
import socket
from datetime import datetime

# create folders
os.makedirs("logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

LOG_FILE = "logs/tamanna_radar.log"
REPORT_FILE = "output/report.json"


def save_log(message, level="INFO"):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_message = f"[{time_now}] [{level}] {message}"

    print(log_message)

    with open(LOG_FILE, "a") as file:
        file.write(log_message + "\n")


def system_info():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    return {
        "hostname": hostname,
        "ip": ip,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def save_report(data):
    with open(REPORT_FILE, "w") as file:
        json.dump(data, file, indent=4)


def monitor():
    save_log("Tamanna Monitor Started")

    while True:
        try:
            info = system_info()

            save_log(f"Monitoring Active | IP: {info['ip']}")

            report = {
                "status": "active",
                "monitor": True,
                "system": info
            }

            save_report(report)

            # suspicious example
            if info["ip"].startswith("127."):
                save_log("Localhost activity detected", "WARNING")

            time.sleep(5)

        except Exception as error:
            save_log(f"Monitor Error: {error}", "ERROR")


# run monitor
monitor()