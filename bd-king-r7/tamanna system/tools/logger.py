import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ----------------------------
# SETTINGS
# ----------------------------
FOLDER_TO_SYNC = "tamanna_system_files"
SYNC_INTERVAL = 60  # seconds
CREDENTIALS_FILE = "credentials.json"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# ----------------------------
# AUTH
# ----------------------------
creds = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
service = build("drive", "v3", credentials=creds)

print("☁️ Tamanna Google Cloud Sync Started")

# ----------------------------
# UPLOAD FUNCTION
# ----------------------------
def upload_file(file_path):
    file_metadata = {"name": os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)

    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print("✅ Uploaded:", file_path)

# ----------------------------
# AUTO SYNC LOOP
# ----------------------------
while True:
    if not os.path.exists(FOLDER_TO_SYNC):
        os.makedirs(FOLDER_TO_SYNC)

    for file in os.listdir(FOLDER_TO_SYNC):
        full_path = os.path.join(FOLDER_TO_SYNC, file)
        if os.path.isfile(full_path):
            upload_file(full_path)

    print("🔄 Sync complete. Sleeping...")
    time.sleep(SYNC_INTERVAL)
import datetime

def log(message):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("system.log", "a") as f:
        f.write(f"[{time}] {message}\n")