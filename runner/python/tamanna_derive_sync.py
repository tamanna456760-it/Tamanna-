#!/usr/bin/env python3
"""Optional PDF-to-Drive sync using JSON credentials, never pickle."""
import os
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def authenticate_drive(credentials_file, token_file):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if token_file.is_file():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_file.is_file():
                raise FileNotFoundError(f"OAuth client file not found: {credentials_file}")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
            creds = flow.run_local_server(port=0)
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(creds.to_json(), encoding="utf-8")
        try:
            token_file.chmod(0o600)
        except OSError:
            pass

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def upload_file(service, file_path, drive_folder_id):
    from googleapiclient.http import MediaFileUpload

    metadata = {"name": file_path.name, "parents": [drive_folder_id]}
    media = MediaFileUpload(str(file_path), mimetype="application/pdf", resumable=True)
    service.files().create(
        body=metadata, media_body=media, fields="id"
    ).execute()


def sync_to_drive(service, books_folder):
    folder_metadata = {
        "name": "Tamanna_AI_Books",
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    drive_folder_id = folder["id"]
    uploaded = 0

    for root, dirs, files in os.walk(books_folder, followlinks=False):
        root_path = Path(root)
        dirs[:] = [
            name for name in dirs
            if not (root_path / name).is_symlink() and not name.startswith(".")
        ]
        for name in files:
            path = root_path / name
            if path.is_symlink() or path.suffix.lower() != ".pdf" or name.startswith("."):
                continue
            upload_file(service, path, drive_folder_id)
            uploaded += 1
    print(f"Uploaded {uploaded} PDF file(s) to Google Drive")


def main():
    if os.environ.get("TAMANNA_ENABLE_DRIVE_SYNC") != "1":
        print("Drive PDF sync disabled; set TAMANNA_ENABLE_DRIVE_SYNC=1 to opt in")
        return

    books_folder = Path(os.environ.get("TAMANNA_BOOKS_FOLDER", "tamanna_ai_books")).expanduser().resolve()
    credentials_file = Path(os.environ.get("TAMANNA_GOOGLE_OAUTH_CLIENT", "")).expanduser()
    token_file = Path(os.environ.get(
        "TAMANNA_GOOGLE_TOKEN_FILE", str(Path.home() / ".tamanna_google_token.json")
    )).expanduser()
    if not books_folder.is_dir():
        raise FileNotFoundError(f"Books folder not found: {books_folder}")
    if not credentials_file.is_file():
        raise FileNotFoundError("Set TAMANNA_GOOGLE_OAUTH_CLIENT to a valid OAuth client JSON file")
    if token_file.resolve() == credentials_file.resolve() or token_file.resolve() in books_folder.parents:
        raise ValueError("Token file must be separate from the OAuth client file and books folder")

    service = authenticate_drive(credentials_file.resolve(), token_file.resolve())
    sync_to_drive(service, books_folder)


if __name__ == "__main__":
    main()
