import json
import time
import os

# 📁 FILES (other system outputs)
ISSUE_FILE = "issues_report.json"
FIX_REPORT = "fix_report.json"
DEFENSE_REPORT = "ai_report.json"
BACKUP_STATE = "ai_backup_db.json"

BRAIN_MEMORY = "brain_memory.json"

📁 backup/
 ├── bd-king-r7_all_backup.py
 ├── r7_backup.py
 ├── bd-king-r7.sql
 └── ssl.sh
📁 tools/
 ├── nmap/
 ├── wireshark/
 ├── smoke.py
 ├── wireshark_automation.py
 └── capture_filter.py
📁 reports/
 ├── issues_report.json
 ├── fix_report.json
 ├── ai_report.json
 ├── ai_backup_db.json
 ├── brain_memory.json
 └── Metadata.json
📁 automation/
 ├── sync_engine.py
 ├── bd-king-r7_max_sync.py
 ├── advanced_sync.py
 ├── ai_sync_controller.py
 ├── auto_fixar.py
 └── problem_fix.json
📁 monitoring/
 ├── system_monitor.py
 ├── system_monitoring.py
 ├── monitoring.py
 ├── uptime_monitor.py
 ├── monitoring.json
📁 models/
 ├── cnn_config.json
 ├── transformer_config.json
 ├── cnn_pattern_detector.py
 ├── rnn_sequence_analyzer.py
 ├── transformer_pattern_engine.py
 ├── lstm_anomaly.py
 ├── autoencoder_anomaly.py
 ├── gan_anomaly_detector.py
 └── time_series_predictor.py
📁 powerhub/
 ├── powerhub_master.py
 ├── run_bd-king-r7_powerhub.py
 ├── monitor.py
 ├── module.py
 ├── self_defence_power.py
 ├── ai_master_power.py
 ├── ai_control.py
 ├── communication_power.py
 ├── Universal_access_power.py
 │
 ├── 📁 scripts/
 │    ├── power.sh
 │    ├── roolback.sh
 │    ├── setup_service.sh
 │
 ├── powerhub.service
 └── ci-cd.yml
📁 website/
 ├── 📁 backend/
 │    ├── server.js
 │    ├── server_main.js
 │    ├── chat.js
 │    ├── auth.js
 │    └── routes/
 │         ├── auth.js
 │         └── chat.js
 │
 ├── 📁 frontend/
 │    ├── index.html
 │    ├── vite.config.js
 │    ├── package.json
 │    └── src/
 │         ├── main.jsx
 │         ├── index.css
 │         ├── apps.jsx
 │         ├── components/navbar.jsx
 │         ├── pages/Home.jsx
 │         └── pages/chat.jsx
 │
 ├── 📁 ai_service/
 │    └── ai_server.js
 │
 ├── 📁 nginx/
 │    └── nginx.conf
 │
 └── 📁 database/
      └── init.sql
📁 src/
 ├── 📁 core/
 │    ├── sync_engine.py
 │    ├── monitoring_system.py
 │    ├── warking.py
 │    ├── decision_maker.py
 │    ├── ai_engine.py
 │    ├── learning_system.py
 │    ├── data_processor.py
 │    └── bd-king-r7.yaml
 │
 ├── 📁 Cybersecurity/
 │    ├── cybersecurity.py
 │    ├── network_defence.py
 │    ├── security_awareness.py
 │    ├── Digital_forensics.py
 │    └── security_hardening.sh
 │
 ├── 📁 database/
 │    ├── schema.sql
 │    ├── bd.json
 │    ├── symptoms_db.json
 │    └── metadata.json
 │
 ├── 📁 map/
 │    ├── bd-king-r7_map.py
 │    └── smoke.py
 │
 ├── 📁 apps/
 │    ├── apps.py
 │    ├── synce.py
 │    ├── ai_sync_controller.py
 │    └── bd-king-r7_ai.py
 │
 ├── 📁 config/
 │    ├── ai_sync_config.json
 │    ├── security.yaml
 │    ├── sync_config.yaml
 │    └── settings.py
 │
 ├── 📁 problem/
 │    └── problem_fix.json
# =========================
# 🧠 LOAD / SAVE
# =========================
def load(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# 🤖 AI DECISION ENGINE
# =========================
def decide_action(file_name, issues, threats):
    if threats:
        return "RESTORE"
    elif issues:
        return "FIX"
    else:
        return "OK"


# =========================
# 📊 ANALYZE ALL SYSTEM
# =========================
def analyze_system():
    issues = load(ISSUE_FILE)
    fixes = load(FIX_REPORT)
    defense = load(DEFENSE_REPORT)
    backup = load(BACKUP_STATE)

    final_report = {}

    all_files = set()

    # collect all files
    for data in [issues, fixes, defense]:
        for item in data:
            all_files.add(item.get("file"))

    for file in all_files:
        file_issues = [i for i in issues if i.get("file") == file]
        file_threats = [d for d in defense if d.get("file") == file and d.get("threats")]

        action = decide_action(file, file_issues, file_threats)

        final_report[file] = {
            "issues": file_issues,
            "threats": file_threats,
            "action": action
        }

    return final_report


# =========================
# 📡 ALERT SYSTEM
# =========================
def alert_system(report):
    for file, data in report.items():
        if data["action"] == "RESTORE":
            print(f"🚨 ALERT: {file} → RESTORED")
        elif data["action"] == "FIX":
            print(f"⚠️ FIX NEEDED: {file}")
        else:
            print(f"✅ OK: {file}")


# =========================
# 🧠 MEMORY LEARNING
# =========================
def update_memory(report):
    memory = load(BRAIN_MEMORY)

    for file, data in report.items():
        memory[file] = {
            "last_action": data["action"],
            "timestamp": time.time()
        }

    save(BRAIN_MEMORY, memory)


# =========================
# 🔁 MAIN LOOP
# =========================
def main():
    while True:
        print("🧠 AI BRAIN ACTIVE...")

        report = analyze_system()
        alert_system(report)
        update_memory(report)

        time.sleep(10)


if __name__ == "__main__":
    main()