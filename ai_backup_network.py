import requests
import base64
import time
import json
import hashlib
import random

# 🔐 CONFIG
GITHUB_TOKEN = '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'
REPO_OWNER = 'tamanna456760-it'
REPO_NAME = 'tamanna-'

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# 📦 Backup Storage
BACKUP_FILE = "ai_backup_db.json"
NETWORK_FILE = "ai_network_state.json"


# =========================
# 📦 LOAD/SAVE SYSTEM
# =========================
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# 🔍 HASH SYSTEM
# =========================
def get_hash(content):
    return hashlib.md5(content.encode()).hexdigest()


# =========================
# 🌐 FETCH FILES
# =========================
def get_repo_files():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return []
    return res.json()


def get_file_content(file):
    res = requests.get(file['url'], headers=HEADERS)
    if res.status_code != 200:
        return None
    data = res.json()
    return base64.b64decode(data['content']).decode('utf-8')


# =========================
# 📦 BACKUP CREATOR (2x AI)
# =========================
def create_dual_backup(path, content, backup_db):
    backup_db[path] = {
        "primary": content,
        "secondary": content[::-1],  # simple mirrored backup
        "hash": get_hash(content)
    }


# =========================
# 🔄 RESTORE SYSTEM
# =========================
def restore_file(path, backup_db):
    if path in backup_db:
        return backup_db[path]["primary"]
    return None


# =========================
# 🤖 AI COMMUNICATION
# =========================
def update_network_state(state):
    save_json(NETWORK_FILE, state)


def broadcast_status(network_state, file, status):
    network_state[file] = {
        "status": status,
        "timestamp": time.time(),
        "node_id": random.randint(1000, 9999)
    }


# =========================
# 🚨 ATTACK DETECTION
# =========================
def detect_attack(content):
    danger = ["rm -rf", "exec(", "eval(", "os.system"]
    return any(d in content for d in danger)


# =========================
# 🔄 UPDATE FILE
# =========================
def update_file(path, content, message):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{tamanna}/contents/{path}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return

    sha = res.json()['sha']

    requests.put(url, headers=HEADERS, json={
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha
    })


# =========================
# 🛡️ MAIN SYSTEM
# =========================
def ai_backup_network():
    backup_db = load_json(BACKUP_FILE)
    network_state = load_json(NETWORK_FILE)

    files = get_repo_files()

    for file in files:
        if file['type'] != 'file':
            continue

        path = file['path']
        content = get_file_content(file)

        if not content:
            continue

        file_hash = get_hash(content)

        # 📦 Create dual backup if not exists
        if path not in backup_db:
            create_dual_backup(path, content, backup_db)

        # 🚨 Attack detection
        if detect_attack(content):
            print(f"🚨 Attack detected: {path}")

            safe_content = restore_file(path, backup_db)

            if safe_content:
                update_file(path, safe_content, "🛡️ Restored from AI Backup")

                broadcast_status(network_state, path, "restored")

        else:
            broadcast_status(network_state, path, "healthy")

    # 💾 Save system state
    save_json(BACKUP_FILE, backup_db)
    update_network_state(network_state)


# =========================
# 🔁 LOOP
# =========================
def main():
    while True:
        print("🌐 AI BACKUP NETWORK RUNNING...")
        ai_backup_network()
        time.sleep(10)


if __name__ == "__main__":
    main()