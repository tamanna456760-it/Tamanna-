import time
import json
import threading
import random

# =========================
# CONFIG
# =========================
MAX_UNITS = 20000  # dynamic increase
CREATE_INTERVAL = 5  # seconds
EMERGENCY_MULTIPLIER = 5  # emergency mode
POWERHUB = "bd-king-r7"

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
    if not nodes:
        nodes = {f"node_{i}": {"power": 100, "status": "active"} for i in range(1, 21)}
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
    unit = {"id": unit_id, "power": power, "status": "active", "timestamp": time.time()}
    units[unit_id] = unit
    save(AI_UNITS_FILE, units)
    print(f"✅ AI UNIT CREATED: {unit_id} | Power: {power}")
    return True


# =========================
# ATTACK DETECTION
# =========================
def attack_detected():
    # Random attack simulation
    return random.choice([False] * 9 + [True])  # 10% chance


def auto_defense(nodes):
    print("🛡️ ATTACK DETECTED → DEFENSE ACTIVATED")
    for node in nodes:
        nodes[node]["power"] += 50  # boost all nodes
    save(NODES_FILE, nodes)
    print("💪 NODES POWER BOOSTED")


# =========================
# MAIN LOOP
# =========================
def ai_network_manager():
    nodes = connect_nodes()
    unit_counter = 1
    emergency_mode = False

    while True:
        if unit_counter % 50 == 0 or attack_detected():  # emergency mode
            emergency_mode = True
        else:
            emergency_mode = False

        # create multiple units in emergency
        units_to_create = 5 if emergency_mode else 1
        for _ in range(units_to_create):
            success = create_ai_unit(f"AI-{unit_counter}", emergency=emergency_mode)
            if not success:
                print("⚠️ MAX UNITS REACHED. Waiting...")
                time.sleep(10)
                continue
            unit_counter += 1

        # distribute power to all nodes
        broadcast_power(nodes, unit_power=5)

        # attack defense auto
        if attack_detected():
            auto_defense(nodes)

        time.sleep(CREATE_INTERVAL)


# =========================
# SELF DECISION MONITOR
# =========================
def self_decision_monitor():
    while True:
        units = load(AI_UNITS_FILE)
        nodes = load(NODES_FILE)
        total_power = sum(nodes[n]["power"] for n in nodes)
        if total_power < 200:
            print("🚨 Low Power Detected → Boosting...")
            broadcast_power(nodes, 50)

        # increase max units dynamically if system strong
        if total_power > 2000 and MAX_UNITS < 50000:
            global MAX_UNITS
            MAX_UNITS += 100
            print(f"⚡ SYSTEM STRONG → MAX UNITS INCREASED: {MAX_UNITS}")
        time.sleep(3)


# =========================
# START SYSTEM
# =========================
if __name__ == "__main__":
    threading.Thread(target=self_decision_monitor, daemon=True).start()
    ai_network_manager()
