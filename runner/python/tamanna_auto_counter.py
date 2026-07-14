import random
import threading
import time

from tamanna_master_attack import (NODES, broadcast_power, create_unit,
                                   save_state)


# =========================
# PREDICTIVE ATTACK & COUNTER
# =========================
def predict_attack(node_name):
    # Calculate attack probability based on past emergency flags
    emergency_flag = NODES[node_name]["emergency"]
    return emergency_flag or random.choice([False] * 7 + [True] * 3)


def auto_counter(node_name):
    if predict_attack(node_name):
        # Boost units proactively
        for _ in range(5):
            create_unit(node_name, emergency=True)
        # Broadcast extra power
        broadcast_power(10)
        # Mark node as defending
        NODES[node_name]["status"] = "auto_defense"
        save_state()


# =========================
# NODE COUNTER THREAD
# =========================
def counter_loop(node_name):
    while True:
        auto_counter(node_name)
        time.sleep(5)  # check every 5 seconds


# =========================
# START ALL COUNTER THREADS
# =========================
def start_auto_counter():
    for node_name in NODES:
        threading.Thread(target=counter_loop, args=(node_name,), daemon=True).start()
