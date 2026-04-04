import threading
import time
import random
import json
from flask import Flask, render_template, jsonify

# =========================
# SYSTEM CONFIG
# =========================
MAX_UNITS = 100000
CREATE_INTERVAL = 2
EMERGENCY_MULTIPLIER = 5
POWERHUB = "bd-king-r7"

NODES = {}
AI_UNITS = {}
NUM_NODES = 20

for i in range(1, NUM_NODES+1):
    NODES[f"node_{i}"] = {"power": 100, "units": 0, "status": "active"}

# =========================
# SAVE / LOAD
# =========================
def save_state():
    with open("nodes_state.json", "w") as f:
        json.dump(NODES, f, indent=2)
    with open("ai_units.json", "w") as f:
        json.dump(AI_UNITS, f, indent=2)

def load_state():
    global NODES, AI_UNITS
    try:
        with open("nodes_state.json", "r") as f:
            NODES.update(json.load(f))
    except:
        pass
    try:
        with open("ai_units.json", "r") as f:
            AI_UNITS.update(json.load(f))
    except:
        pass

# =========================
# NODE FUNCTIONS
# =========================
def broadcast_power(amount):
    for node in NODES:
        NODES[node]["power"] += amount

def create_unit(node_name, emergency=False):
    global AI_UNITS
    if len(AI_UNITS) >= MAX_UNITS:
        return
    unit_id = f"AI-{len(AI_UNITS)+1}"
    power = 10 * (EMERGENCY_MULTIPLIER if emergency else 1)
    AI_UNITS[unit_id] = {"power": power, "controlled_by": node_name, "status": "active"}
    NODES[node_name]["units"] += 1

def attack_detected(node_name):
    return random.choice([False]*8 + [True]*2)

def auto_defense(node_name):
    NODES[node_name]["status"] = "active"
    NODES[node_name]["power"] += 50

# =========================
# NODE THREAD
# =========================
def node_loop(node_name):
    while True:
        emergency = attack_detected(node_name)
        units_to_create = 5 if emergency else 1
        for _ in range(units_to_create):
            create_unit(node_name, emergency)
        if emergency:
            auto_defense(node_name)
        broadcast_power(5)
        save_state()
        time.sleep(CREATE_INTERVAL)

# =========================
# FLASK DASHBOARD
# =========================
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/status")
def status():
    return jsonify({
        "nodes": NODES,
        "units": AI_UNITS,
        "total_units": len(AI_UNITS)
    })

# =========================
# START SYSTEM
# =========================
if __name__ == "__main__":
    load_state()
    # Start all nodes
    for node_name in NODES:
        threading.Thread(target=node_loop, args=(node_name,), daemon=True).start()
    # Start web dashboard
    app.run(host="0.0.0.0", port=5000)