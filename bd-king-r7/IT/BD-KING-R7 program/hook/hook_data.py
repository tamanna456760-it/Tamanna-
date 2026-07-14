#!/usr/bin/env python3

import json
import os
import socket
import time
from datetime import datetime

import psutil

CONFIG = {
    "interval_seconds": 10,
    "report_file": "master_hook_data.json",
    "data_log_file": "collected_dataset.jsonl",
}

# ==========================
# TIME
# ==========================


def now():
    return datetime.utcnow().isoformat()


# ==========================
# SYSTEM DATA COLLECTOR
# ==========================


def collect_system_data():
    return {
        "timestamp": now(),
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "process_count": len(psutil.pids()),
    }


# ==========================
# NETWORK DATA COLLECTOR
# ==========================


def collect_network_data():
    net = psutil.net_io_counters()
    hostname = socket.gethostname()

    return {
        "timestamp": now(),
        "hostname": hostname,
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv,
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
    }


# ==========================
# PROCESS DATA COLLECTOR
# ==========================


def collect_process_data():
    processes = []

    for p in psutil.process_iter(
        attrs=["pid", "name", "cpu_percent", "memory_percent"]
    ):
        try:
            processes.append(p.info)
        except:
            pass

    return {"timestamp": now(), "top_processes": processes[:10]}


# ==========================
# FILE ACTIVITY COLLECTOR (basic scan)
# ==========================


def collect_file_data(path="."):
    files = []

    for root, dirs, filenames in os.walk(path):
        for f in filenames[:20]:
            files.append(
                {
                    "file": os.path.join(root, f),
                    "size": os.path.getsize(os.path.join(root, f)),
                }
            )

        break  # shallow scan only

    return {"timestamp": now(), "files": files}


# ==========================
# DATA STORAGE
# ==========================


def save_jsonl(data):
    with open(CONFIG["data_log_file"], "a") as f:
        f.write(json.dumps(data) + "\n")


# ==========================
# MASTER COLLECTOR ENGINE
# ==========================


def run_collector():
    dataset = {
        "system": collect_system_data(),
        "network": collect_network_data(),
        "process": collect_process_data(),
        "file": collect_file_data(),
    }

    save_jsonl(dataset)

    with open(CONFIG["report_file"], "w") as f:
        json.dump(dataset, f, indent=4)

    print("📊 Data Collected:", dataset["system"]["timestamp"])


# ==========================
# LOOP
# ==========================

if __name__ == "__main__":
    while True:
        try:
            run_collector()
            time.sleep(CONFIG["interval_seconds"])

        except KeyboardInterrupt:
            print("Stopped.")
            break

        except Exception as e:
            print("Error:", str(e))
