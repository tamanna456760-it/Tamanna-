import os
import time
import hashlib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ---------------- SETTINGS ----------------
SYNC_FOLDER = "tamanna"
LOG_FILE = "sync_log.txt"
SYNC_INTERVAL = 60  # seconds
CREDENTIALS_FILE = "credentials.json"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# ---------------- AUTH ----------------
creds = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
drive = build("drive", "v3", credentials=creds)

print("☁️ Tamanna Advanced Sync Started")

# ---------------- HASH SYSTEM ----------------
file_hashes = {}

def get_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

# ---------------- LOG ----------------
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

# ---------------- UPLOAD ----------------
def upload_file(path):
    try:
        file_name = os.path.basename(path)
        media = MediaFileUpload(path, resumable=True)
        drive.files().create(
            body={"name": file_name},
            media_body=media,
            fields="id"
        ).execute()

        log(f"✅ Uploaded: {path}")
    except Exception as e:
        log(f"❌ Error uploading {path}: {e}")

# ---------------- SYNC LOOP ----------------
while True:
    for root, dirs, files in os.walk(SYNC_FOLDER):
        for file in files:
            full_path = os.path.join(root, file)
            current_hash = get_hash(full_path)

            if full_path not in file_hashes:
                file_hashes[full_path] = current_hash
                upload_file(full_path)

            elif file_hashes[full_path] != current_hash:
                file_hashes[full_path] = current_hash
                upload_file(full_path)

    log("🔄 Sync cycle complete")
    time.sleep(SYNC_INTERVAL)