import hashlib
import json
import os
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ================= CONFIG =================
SYNC_FOLDER = "tamanna"
STATE_FILE = "tamanna_code.py"
LOG_FILE = "sync_log.txt"
ZIP_FOLDER = "temp_zip"
SYNC_INTERVAL = 20
THREADS = 4
DRY_RUN = False  # True = test mode
CREDENTIALS_FILE = "credentials.json"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# ================= AUTH =================
creds = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
drive = build("drive", "v3", credentials=creds)

# ================= UTIL =================
os.makedirs(ZIP_FOLDER, exist_ok=True)

def log(msg):
    line = f"[{datetime.now()}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def zip_file(src, rel):
    zip_path = os.path.join(ZIP_FOLDER, rel.replace("/", "_") + ".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(src, arcname=os.path.basename(src))
    return zip_path

# ================= LOAD STATE =================
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {}

# ================= UPLOAD =================
def upload_task(full_path, rel_path):
    try:
        file_hash = sha256(full_path)

        if rel_path in state and state[rel_path] == file_hash:
            return

        zip_path = zip_file(full_path, rel_path)

        if DRY_RUN:
            log(f"🧪 DRY-RUN: {rel_path}")
            state[rel_path] = file_hash
            return

        media = MediaFileUpload(zip_path, resumable=True)
        drive.files().create(
            body={"name": rel_path + ".zip"},
            media_body=media,
            fields="id"
        ).execute()

        state[rel_path] = file_hash
        log(f"⚡ UPLOADED: {rel_path}")

    except Exception as e:
        log(f"❌ ERROR {rel_path}: {e}")

# ================= MAIN LOOP =================
log("🔥 TAMANNA ULTRA POWER MODE STARTED")

while True:
    tasks = []
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for root, dirs, files in os.walk(SYNC_FOLDER):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, SYNC_FOLDER)
                tasks.append(executor.submit(upload_task, full_path, rel_path))

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    log("🚀 ULTRA SYNC CYCLE COMPLETE")
    time.sleep(SYNC_INTERVAL)