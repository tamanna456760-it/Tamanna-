import base64
import hashlib
import time

import requests

GITHUB_TOKEN = "তোমার_গিটহাব_টোকেন"
REPO_OWNER = "tamanna456760-it"
REPO_NAME = "tamanna-"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# 🚨 Suspicious keywords (danger detection)
DANGEROUS_KEYWORDS = [
    "os.system",
    "rm -rf",
    "subprocess",
    "eval(",
    "exec(",
    "chmod 777",
    "requests.post(",
]

# 📦 Backup storage
backup_store = {}


def generate_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()


def is_dangerous(code):
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in code:
            return True
    return False


def backup_file(path, content):
    backup_store[path] = content


def restore_file(path):
    return backup_store.get(path, None)


def report_to_ai_master(data):
    ai_master_url = "https://example.com/ai/security_report"
    try:
        requests.post(ai_master_url, json=data)
    except:
        print("AI Master communication failed")


def scan_and_protect():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("❌ Repo access failed")
        return

    files = response.json()
    report = []

    for file in files:
        if file["type"] == "file":
            file_url = file["url"]
            res = requests.get(file_url, headers=HEADERS)

            if res.status_code != 200:
                continue

            data = res.json()
            content = base64.b64decode(data["content"]).decode("utf-8")

            file_hash = generate_hash(content)

            # 📦 Backup first time
            if file["path"] not in backup_store:
                backup_file(file["path"], content)

            # 🚨 Detect dangerous code
            if is_dangerous(content):
                print(f"⚠️ Dangerous code detected in {file['path']}")

                safe_content = restore_file(file["path"])

                if safe_content:
                    update_file(file["path"], safe_content, "Restore safe version")

                    report.append(
                        {"file": file["path"], "status": "restored (danger detected)"}
                    )
                else:
                    report.append(
                        {"file": file["path"], "status": "danger detected (no backup)"}
                    )
            else:
                report.append({"file": file["path"], "status": "safe"})

    report_to_ai_master(report)


def update_file(path, new_content, message):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"

    get_res = requests.get(url, headers=HEADERS)
    if get_res.status_code != 200:
        return

    sha = get_res.json()["sha"]

    requests.put(
        url,
        headers=HEADERS,
        json={
            "message": message,
            "content": base64.b64encode(new_content.encode()).decode(),
            "sha": sha,
        },
    )


if __name__ == "__main__":
    while True:
        print("🛡️ AI Self Defense Running...")
        scan_and_protect()
        time.sleep(10)
