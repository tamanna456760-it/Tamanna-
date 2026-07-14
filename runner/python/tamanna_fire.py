import hashlib
import json
import os
import time
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ================= SETTINGS =================
SYNC_FOLDER = "tamanna_data"
STATE_FILE = "sync_state.json"
LOG_FILE = "sync_log.txt"
SYNC_INTERVAL = 30  # seconds
DRY_RUN = False  # True = test mode, False = real upload
CREDENTIALS_FILE = "credentials.json"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# ================= AUTH =================
creds = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
drive = build("drive", "v3", credentials=creds)

print("🔥 TAMANNA FIRE MODE SYNC STARTED")


# ================= HELPERS =================
def log(msg):
    line = f"[{datetime.now()}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


# ================= LOAD STATE =================
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {}


# ================= UPLOAD =================
def upload(path, rel_path):
    if DRY_RUN:
        log(f"🧪 DRY-RUN: {rel_path}")
        return

    media = MediaFileUpload(path, resumable=True)
    drive.files().create(
        body={"name": rel_path}, media_body=media, fields="id"
    ).execute()

    log(f"🚀 UPLOADED: {rel_path}")


# ================= FIRE SYNC LOOP =================
while True:
    for root, dirs, files in os.walk(SYNC_FOLDER):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, SYNC_FOLDER)
            current_hash = file_hash(full_path)

            if rel_path not in state:
                upload(full_path, rel_path)
                state[rel_path] = current_hash

            elif state[rel_path] != current_hash:
                upload(full_path, rel_path)
                state[rel_path] = current_hash

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    log("🔥 FIRE MODE SYNC CYCLE COMPLETE")
    time.sleep(SYNC_INTERVAL)
