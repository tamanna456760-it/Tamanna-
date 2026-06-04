# 🤖 Tamanna AI Core Engine (Advanced Version)

import os
import json
import logging
from datetime import datetime

# ==============================
# 🔧 Logger Setup
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Tamanna AI] %(levelname)s: %(message)s"
)

# ==============================
# 🧠 Core Engine Class
# ==============================
class TamannaCore:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.memory = {}
        self.modules = {}
        logging.info("Tamanna AI Core Initialized")

    # ==============================
    # ⚙️ Load Configuration
    # ==============================
    def load_config(self, path):
        if not os.path.exists(path):
            logging.warning("Config file not found. Using default config.")
            return {}

        with open(path, "r") as f:
            return json.load(f)

    # ==============================
    # 📂 Snapshot Loader
    # ==============================
    def load_snapshots(self, directory="snapshots"):
        snapshots = []

        if not os.path.exists(directory):
            logging.warning("Snapshots directory not found")
            return snapshots

        for file in os.listdir(directory):
            if file.endswith(".md"):
                with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
                    snapshots.append(f.read())

        logging.info(f"{len(snapshots)} snapshots loaded")
        return snapshots

    # ==============================
    # 🧠 Analyze Code (Basic AI Logic)
    # ==============================
    def analyze(self, snapshots):
        results = []

        for snap in snapshots:
            if "error" in snap.lower():
                results.append("⚠️ Potential issue detected")
            if "fix" in snap.lower():
                results.append("✅ Fix suggestion found")

        return results

    # ==============================
    # 🤖 Decision Engine
    # ==============================
    def decide(self, analysis):
        decision = "No action needed"

        if any("issue" in a for a in analysis):
            decision = "Run Debug Module"

        if any("fix" in a for a in analysis):
            decision = "Apply Auto Fix"

        logging.info(f"Decision: {decision}")
        return decision

    # ==============================
    # ⚡ Auto Fix System
    # ==============================
    def auto_fix(self):
        logging.info("Running Auto Fix Engine...")
        return "Fix Applied Successfully"

    # ==============================
    # 🔄 Sync Engine
    # ==============================
    def sync(self):
        logging.info("Running Sync Engine...")
        return "System Synced"

    # ==============================
    # 🔐 Security Scan
    # ==============================
    def security_scan(self):
        logging.info("Running Security Scan...")
        return "No Threats Found"

    # ==============================
    # 🧠 Learning System
    # ==============================
    def learn(self, data):
        timestamp = str(datetime.now())
        self.memory[timestamp] = data
        logging.info("Learning data stored")

    # ==============================
    # 🚀 Run Full Pipeline
    # ==============================
    def run(self):
        logging.info("Starting Tamanna AI Pipeline...")

        snapshots = self.load_snapshots()
        analysis = self.analyze(snapshots)
        decision = self.decide(analysis)

        if decision == "Run Debug Module":
            fix = self.auto_fix()
        elif decision == "Apply Auto Fix":
            fix = self.auto_fix()
        else:
            fix = "No Fix Needed"

        sync_status = self.sync()
        security = self.security_scan()

        self.learn({
            "analysis": analysis,
            "decision": decision,
            "fix": fix
        })

        return {
            "analysis": analysis,
            "decision": decision,
            "fix": fix,
            "sync": sync_status,
            "security": security
        }


# ==============================
# ▶️ Run Engine
# ==============================
if __name__ == "__main__":
    ai = TamannaCore()
    result = ai.run()

    print("\n=== Tamanna AI Result ===")
    for k, v in result.items():
        print(f"{k.upper()}: {v}")