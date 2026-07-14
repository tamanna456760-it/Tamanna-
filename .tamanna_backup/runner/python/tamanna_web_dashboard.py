import json
import random
import threading
import time

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# =========================
# MASTER AI CONFIG
# =========================
MASTER_AI = "Tamanna"
MAX_UNITS = 100000
CREATE_INTERVAL = 2  # seconds
EMERGENCY_MULTIPLIER = 5
POWERHUB = "bd-king-r7"

# =========================
# SIMULATED NODES
# =========================
NODES = {
    f"node_{i}": {"power": 100, "units": 0, "status": "active"} for i in range(1, 21)
}
AI_UNITS = {}


# =========================
# SAVE / LOAD STATE
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
# NODE COMMUNICATION
# =========================
def broadcast_power(amount):
    for node in NODES:
        NODES[node]["power"] += amount


# =========================
# UNIT CREATION
# =========================
def create_unit(emergency=False):
    global AI_UNITS
    if len(AI_UNITS) >= MAX_UNITS:
        return
    unit_id = f"AI-{len(AI_UNITS)+1}"
    power = 10 * (EMERGENCY_MULTIPLIER if emergency else 1)
    AI_UNITS[unit_id] = {"power": power, "controlled_by": MASTER_AI, "status": "active"}
    node = random.choice(list(NODES.keys()))
    NODES[node]["units"] += 1


# =========================
# ATTACK DETECTION
# =========================
def attack_detected():
    return random.choice([False] * 8 + [True] * 2)


def auto_defense():
    broadcast_power(50)
    for node in NODES:
        NODES[node]["status"] = "active"


# =========================
# MASTER AI LOOP
# =========================
def master_ai_loop():
    while True:
        emergency = attack_detected()
        units_to_create = 5 if emergency else 1
        for _ in range(units_to_create):
            create_unit(emergency)
        if emergency:
            auto_defense()
        broadcast_power(5)
        save_state()
        time.sleep(CREATE_INTERVAL)


# =========================
# API ENDPOINTS FOR DASHBOARD
# =========================
@app.route("/api/status")
def api_status():
    return jsonify({"nodes": NODES, "ai_units": len(AI_UNITS)})


@app.route("/")
def dashboard():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tamanna AI Dashboard</title>
        <style>
            body {font-family: Arial; background:#111; color:#0f0;}
            .node {border:1px solid #0f0; margin:5px; padding:5px;}
        </style>
        <script>
        async function fetchStatus(){
            const res = await fetch("/api/status");
            const data = await res.json();
            const container = document.getElementById("nodes");
            container.innerHTML = "";
            for (const node in data.nodes){
                const n = data.nodes[node];
                const div = document.createElement("div");
                div.className = "node";
                div.innerHTML = `<b>${node}</b> | Power: ${n.power} | Units: ${n.units} | Status: ${n.status}`;
                container.appendChild(div);
            }
            document.getElementById("total_units").innerText = "Total AI Units: " + data.ai_units;
        }
        setInterval(fetchStatus, 2000);
        window.onload = fetchStatus;
        </script>
    </head>
    <body>
        <h1>Tamanna AI Dashboard</h1>
        <div id="total_units"></div>
        <div id="nodes"></div>
    </body>
    </html>
    """
    return render_template_string(html)


# =========================
# START SIMULATION
# =========================
if __name__ == "__main__":
    load_state()
    threading.Thread(target=master_ai_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
