import os, pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def drive_service():
    creds = None
    if os.path.exists("token.pickle"):
        creds = pickle.load(open("token.pickle", "rb"))

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        pickle.dump(creds, open("token.pickle", "wb"))

    return build("drive", "v3", credentials=creds)

def upload_books():
    service = drive_service()
    for root, _, files in os.walk("tamanna_ai_books"):
        for f in files:
            if f.endswith(".pdf"):
                path = os.path.join(root, f)
                media = MediaFileUpload(path)
                service.files().create(body={"name": f}, media_body=media).execute()
                print(f"☁ Uploaded: {f}")