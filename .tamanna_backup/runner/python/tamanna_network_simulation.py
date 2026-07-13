import time
import threading
import random
import json

# =========================
# MASTER CONFIG
# =========================
MASTER_AI = "Tamanna"
MAX_UNITS = 5000
CREATE_INTERVAL = 2  # seconds
EMERGENCY_MULTIPLIER = 5
POWERHUB = "bd-king-r7"

# =========================
# SIMULATED NODES
# =========================
NODES = {
    f"node_{i}": {"power": 100, "units": 0, "status": "active"} for i in range(1, 11)
}

AI_UNITS = {}

# =========================
# SAVE / LOAD FUNCTIONS
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
            NODES = json.load(f)
    except:
        pass
    try:
        with open("ai_units.json", "r") as f:
            AI_UNITS = json.load(f)
    except:
        pass

# =========================
# NODE COMMUNICATION
# =========================
def broadcast_power(amount):
    for node in NODES:
        NODES[node]["power"] += amount
    print(f"📡 [{MASTER_AI}] Broadcasting {amount} power to all nodes")

# =========================
# UNIT CREATION
# =========================
def create_unit(emergency=False):
    global AI_UNITS
    if len(AI_UNITS) >= MAX_UNITS:
        print(f"⚠️ [{MASTER_AI}] MAX UNITS REACHED")
        return
    unit_id = f"AI-{len(AI_UNITS)+1}"
    power = 10 * (EMERGENCY_MULTIPLIER if emergency else 1)
    AI_UNITS[unit_id] = {"power": power, "controlled_by": MASTER_AI, "status": "active"}
    # Assign unit to a random node
    node = random.choice(list(NODES.keys()))
    NODES[node]["units"] += 1
    print(f"✅ [{MASTER_AI}] Created {unit_id} | Power: {power} | Assigned to {node}")

# =========================
# ATTACK DETECTION & DEFENSE
# =========================
def attack_detected():
    return random.choice([False]*8 + [True]*2)

def auto_defense():
    print(f"🛡️ [{MASTER_AI}] ATTACK DETECTED → DEFENSE ACTIVATED")
    broadcast_power(50)
    for node in NODES:
        NODES[node]["status"] = "active"

# =========================
# MASTER AI NETWORK LOOP
# =========================
def master_ai_loop():
    unit_counter = 1
    while True:
        emergency = attack_detected()
        units_to_create = 5 if emergency else 1
        for _ in range(units_to_create):
            create_unit(emergency)
            unit_counter += 1
        if emergency:
            auto_defense()
        broadcast_power(5)
        save_state()
        time.sleep(CREATE_INTERVAL)

# =========================
# REAL-TIME MONITOR
# =========================
def monitor_loop():
    while True:
        print("\n=== SYSTEM STATUS ===")
        for node, data in NODES.items():
            print(f"{node}: Power={data['power']} | Units={data['units']} | Status={data['status']}")
        print(f"Total AI Units: {len(AI_UNITS)}\n")
        time.sleep(5)

# =========================
# START SIMULATION
# =========================
if __name__ == "__main__":
    load_state()
    print(f"🤖 [{MASTER_AI}] DISTRIBUTED AI NETWORK SIMULATION ONLINE")
    threading.Thread(target=monitor_loop, daemon=True).start()
    master_ai_loop()