"""Optional Google Drive upload support for the local Tamanna book library.

No credentials or API keys are stored in this repository. Configure the OAuth
client and token paths on the private server before enabling uploads.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def upload_books() -> dict[str, Any]:
    """Upload local book files to a configured Google Drive folder.

    Returns a skipped status when private OAuth configuration is incomplete.
    The first OAuth authorization may open a local browser; unattended servers
    should provision a valid token file out of band.
    """
    folder_id = os.getenv("TAMANNA_GOOGLE_DRIVE_FOLDER_ID", "").strip()
    client_file = Path(os.getenv("TAMANNA_GOOGLE_CLIENT_SECRETS_FILE", "")).expanduser()
    token_file = Path(os.getenv("TAMANNA_GOOGLE_TOKEN_FILE", "data/google_drive_token.json")).expanduser()
    books_dir = Path(os.getenv("TAMANNA_BOOKS_DIR", Path(__file__).resolve().parents[1] / "data" / "books")).expanduser()

    if not folder_id or not client_file.is_file():
        return {"status": "skipped", "reason": "Google Drive folder ID or OAuth client file is not configured."}

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        return {"status": "error", "reason": f"Google Drive dependencies unavailable: {type(exc).__name__}"}

    credentials = None
    if token_file.is_file():
        try:
            credentials = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        except (OSError, ValueError):
            credentials = None

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    if not credentials or not credentials.valid:
        # TODO: For unattended deployments, provision a valid OAuth token securely instead of interactive consent.
        flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
        credentials = flow.run_local_server(port=0)
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(credentials.to_json(), encoding="utf-8")
        try:
            token_file.chmod(0o600)
        except OSError:
            pass

    if not books_dir.is_dir():
        return {"status": "skipped", "reason": "Local books directory does not exist."}

    service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    uploaded = []
    for path in sorted(item for item in books_dir.rglob("*") if item.is_file()):
        metadata = {"name": path.name, "parents": [folder_id]}
        media = MediaFileUpload(str(path), resumable=True)
        result = service.files().create(body=metadata, media_body=media, fields="id,name").execute()
        uploaded.append({"id": result.get("id"), "name": result.get("name")})
    return {"status": "ok", "uploaded": len(uploaded), "files": uploaded}


__all__ = ["upload_books"]
