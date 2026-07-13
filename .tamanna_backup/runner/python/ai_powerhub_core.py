import time
import json
import threading
import random

# =========================
# CONFIG
# =========================
MAX_UNITS = 10000
CREATE_INTERVAL = 5  # seconds
EMERGENCY_MULTIPLIER = 3  # emergency mode
POWERHUB = "bd-king-r7"  # central power source

# =========================
# MEMORY FILES
# =========================
NODES_FILE = "nodes_status.json"
AI_UNITS_FILE = "ai_units.json"

# =========================
# LOAD / SAVE
# =========================
def load(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# =========================
# NODE MANAGEMENT
# =========================
def connect_nodes():
    nodes = load(NODES_FILE)
    # simulate 10 nodes if empty
    if not nodes:
        nodes = {f"node_{i}": {"power": 100, "status": "active"} for i in range(1, 11)}
        save(NODES_FILE, nodes)
    return nodes

def broadcast_power(nodes, unit_power):
    for node in nodes:
        nodes[node]["power"] += unit_power
    save(NODES_FILE, nodes)

# =========================
# AI UNIT CREATION
# =========================
def create_ai_unit(unit_id, emergency=False):
    units = load(AI_UNITS_FILE)
    if len(units) >= MAX_UNITS:
        return False  # max reached
    power = 10
    if emergency:
        power *= EMERGENCY_MULTIPLIER
    unit = {
        "id": unit_id,
        "power": power,
        "status": "active",
        "timestamp": time.time()
    }
    units[unit_id] = unit
    save(AI_UNITS_FILE, units)
    print(f"✅ AI UNIT CREATED: {unit_id} | Power: {power}")
    return True

# =========================
# MAIN LOOP
# =========================
def ai_network_manager():
    nodes = connect_nodes()
    unit_counter = 1
    emergency_mode = False

    while True:
        if unit_counter % 50 == 0:  # simulate emergency every 50 units
            emergency_mode = True
        else:
            emergency_mode = False

        success = create_ai_unit(f"AI-{unit_counter}", emergency=emergency_mode)
        if not success:
            print("⚠️ MAX UNITS REACHED. Waiting...")
            time.sleep(10)
            continue

        # distribute power to all nodes
        broadcast_power(nodes, unit_power=5)
        unit_counter += 1
        time.sleep(CREATE_INTERVAL)


# =========================
# MULTI THREAD / SELF DECISION
# =========================
def self_decision_monitor():
    while True:
        units = load(AI_UNITS_FILE)
        nodes = load(NODES_FILE)
        total_power = sum(nodes[n]["power"] for n in nodes)
        if total_power < 200:
            print("🚨 Low Power Detected → Boosting...")
            broadcast_power(nodes, 50)
        # additional decision logic can go here
        time.sleep(3)

# =========================
# START SYSTEM
# =========================
if __name__ == "__main__":
    threading.Thread(target=self_decision_monitor, daemon=True).start()
    ai_network_manager()