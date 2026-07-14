import requests
import base64
import hashlib
import time
import json

# 🔐 CONFIG
GITHUB_TOKEN = "tamanna"
REPO_OWNER = "tamanna456760-it"
REPO_NAME = "tamanna-"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# 🚨 Dangerous patterns
DANGEROUS_PATTERNS = [
    "os.system",
    "rm -rf",
    "subprocess",
    "eval(",
    "exec(",
    "chmod 777",
    "requests.post(",
    "socket",
    "pickle.loads",
]

# 📦 Backup DB
backup_db = {}

# 📊 Shared AI Memory
AI_MEMORY_FILE = "ai_memory.json"


# ==============================
# 🧠 MEMORY SYSTEM
# ==============================
def load_memory():
    try:
        with open(AI_MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_memory(data):
    with open(AI_MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ==============================
# 🔍 HASH SYSTEM
# ==============================
def get_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()


# ==============================
# 🚨 DETECTION ENGINE
# ==============================
def detect_threat(code):
    issues = []
    for pattern in DANGEROUS_PATTERNS:
        if pattern in code:
            issues.append(pattern)
    return issues


# ==============================
# 📦 BACKUP SYSTEM
# ==============================
def backup_file(path, content):
    backup_db[path] = content


def restore_backup(path):
    return backup_db.get(path, None)


# ==============================
# 🔄 GITHUB FILE UPDATE
# ==============================
def update_file(path, content, message):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        return

    sha = res.json()["sha"]

    requests.put(
        url,
        headers=HEADERS,
        json={
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "sha": sha,
        },
    )


# ==============================
# 🤖 AI COMMUNICATION
# ==============================
def send_to_ai_system(report):
    try:
        with open("ai_report.json", "w") as f:
            json.dump(report, f, indent=2)
    except:
        pass


# ==============================
# 🔍 FULL REPO SCAN
# ==============================
def scan_repo():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        print("❌ Repo access error")
        return []

    return res.json()


# ==============================
# 🛡️ DEFENSE CORE ENGINE
# ==============================
def defense_engine():
    files = scan_repo()
    memory = load_memory()
    report = []

    for file in files:
        if file["type"] != "file":
            continue

        file_url = file["url"]
        res = requests.get(file_url, headers=HEADERS)

        if res.status_code != 200:
            continue

        data = res.json()
        content = base64.b64decode(data["content"]).decode("utf-8")

        file_hash = get_hash(content)

        # 📦 Backup first
        if file["path"] not in backup_db:
            backup_file(file["path"], content)

        # 🔍 Detect threats
        threats = detect_threat(content)

        if threats:
            print(f"🚨 Threat in {file['path']} → {threats}")

            safe_content = restore_backup(file["path"])

            if safe_content:
                update_file(file["path"], safe_content, "🛡️ Auto Restore Safe Version")

                status = "restored"
            else:
                status = "no backup"

        else:
            status = "safe"

        # 🧠 Memory update
        memory[file["path"]] = {"hash": file_hash, "status": status, "threats": threats}

        report.append({"file": file["path"], "status": status, "threats": threats})

    save_memory(memory)
    send_to_ai_system(report)


# ==============================
# 🔁 LOOP RUNNER
# ==============================
def main():
    while True:
        print("🛡️ AI DEFENSE CORE RUNNING...")
        defense_engine()
        time.sleep(10)


if __name__ == "__main__":
    main()
