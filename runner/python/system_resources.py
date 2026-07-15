# system_resources.py
import datetime

import psutil


def log_system_status():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    with open("../logs/system_resources.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} | CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%\n")

if __name__ == "__main__":
    log_system_status()
    print("System resource monitoring complete.")