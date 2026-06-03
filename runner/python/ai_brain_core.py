import json
import time
import os

# 📁 FILES (other system outputs)
ISSUE_FILE = "issues_report.json"
FIX_REPORT = "fix_report.json"
DEFENSE_REPORT = "ai_report.json"
BACKUP_STATE = "ai_backup_db.json"

BRAIN_MEMORY = "brain_memory.json"


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