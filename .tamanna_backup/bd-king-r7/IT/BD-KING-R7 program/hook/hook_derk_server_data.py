#!/usr/bin/env python3

import psutil
import json
import time
import socket
from datetime import datetime

CONFIG = {"interval": 5, "output_file": "dark_server_hook.jsonl"}

# =========================
# TIME
# =========================


def ts():
    return datetime.utcnow().isoformat()


# =========================
# SERVER CORE DATA
# =========================


def server_data():
    return {
        "time": ts(),
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "process_count": len(psutil.pids()),
    }


# =========================
# NETWORK DATA
# =========================


def network_data():
    net = psutil.net_io_counters()
    host = socket.gethostname()

    return {
        "time": ts(),
        "host": host,
        "sent": net.bytes_sent,
        "recv": net.bytes_recv,
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
    }


# =========================
# PROCESS INTELLIGENCE
# =========================


def process_data():
    top = []

    for p in psutil.process_iter(
        attrs=["pid", "name", "cpu_percent", "memory_percent"]
    ):
        try:
            top.append(p.info)
        except:
            pass

    top = sorted(top, key=lambda x: x.get("cpu_percent", 0), reverse=True)

    return {"time": ts(), "top_processes": top[:10]}


# =========================
# ANOMALY DETECTOR
# =========================


def anomaly_check(system):
    alerts = []

    if system["cpu"] > 85:
        alerts.append("HIGH CPU USAGE")

    if system["ram"] > 80:
        alerts.append("HIGH MEMORY USAGE")

    if system["disk"] > 90:
        alerts.append("LOW DISK SPACE")

    return alerts if alerts else ["SYSTEM NORMAL"]


# =========================
# DATA WRITER
# =========================


def write(data):
    with open(CONFIG["output_file"], "a") as f:
        f.write(json.dumps(data) + "\n")


# =========================
# MAIN HOOK ENGINE
# =========================


def run_dark_hook():
    system = server_data()
    network = network_data()
    process = process_data()
    alerts = anomaly_check(system)

    payload = {
        "system": system,
        "network": network,
        "process": process,
        "alerts": alerts,
    }

    write(payload)

    print("🖤 DARK HOOK ACTIVE:", system["time"])
    print("Alerts:", alerts)


# =========================
# LOOP
# =========================

if __name__ == "__main__":
    while True:
        try:
            run_dark_hook()
            time.sleep(CONFIG["interval"])

        except KeyboardInterrupt:
            print("Stopped.")
            break

        except Exception as e:
            print("Error:", e)
