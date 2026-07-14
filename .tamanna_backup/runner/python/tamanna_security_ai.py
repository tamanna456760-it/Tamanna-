import json
import random
import threading
import time

from tamanna_master_attack import (NODES, broadcast_power, create_unit,
                                   save_state)

# =========================
# SECURITY LOG FILE
# =========================
LOG_FILE = "security_logs.json"


def log_event(event):
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    logs.append({"time": time.ctime(), "event": event})
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


# =========================
# INTRUSION DETECTION
# =========================
def detect_intrusion(node_name):
    # Simulated suspicious activity
    suspicious = random.choice([False] * 7 + [True] * 3)
    if suspicious:
        log_event(f"⚠️ Intrusion detected on {node_name}")
    return suspicious


# =========================
# AUTO DEFENSE SYSTEM
# =========================
def auto_protect(node_name):
    print(f"🛡️ [SECURITY AI] Protecting {node_name}")

    # Boost power
    NODES[node_name]["power"] += 100

    # Create defense units
    for _ in range(3):
        create_unit(node_name, emergency=True)

    # Broadcast alert
    broadcast_power(20)

    # Log action
    log_event(f"🛡️ Defense activated on {node_name}")
    save_state()


# =========================
# NETWORK-WIDE ALERT
# =========================
def global_alert(node_name):
    print(f"🚨 ALERT: Attack spreading from {node_name}")
    for node in NODES:
        NODES[node]["status"] = "alert"
    log_event(f"🚨 Global alert triggered by {node_name}")


# =========================
# SECURITY LOOP
# =========================
def security_loop():
    while True:
        for node in NODES:
            if detect_intrusion(node):
                auto_protect(node)
                global_alert(node)
        time.sleep(5)


# =========================
# START SECURITY SYSTEM
# =========================
def start_security_ai():
    threading.Thread(target=security_loop, daemon=True).start()
