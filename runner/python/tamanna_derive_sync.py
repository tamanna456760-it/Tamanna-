import os
import pickle
import requests
from tqdm import tqdm
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Path to the folder with PDFs
BOOKS_FOLDER = "tamanna_ai_books"

def authenticate_drive():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("drive", "v3", credentials=creds)
    return service

def upload_file(service, file_path, drive_folder_id=None):
    file_name = os.path.basename(file_path)
    file_metadata = {"name": file_name}
    if drive_folder_id:
        file_metadata["parents"] = [drive_folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"☁ Uploaded: {file_name}")

def sync_to_drive(service):
    # Optional: Create Drive folder
    folder_metadata = {
        "name": "Tamanna_AI_Books",
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    drive_folder_id = folder.get("id")
    print("📁 Drive folder created:", drive_folder_id)

    # Upload all PDFs
    for root, dirs, files in os.walk(BOOKS_FOLDER):
        for file in files:
            if file.endswith(".pdf"):
                upload_file(service, os.path.join(root, file), drive_folder_id)

def main():
    service = authenticate_drive()
    sync_to_drive(service)

if __name__ == "__main__":
    main()