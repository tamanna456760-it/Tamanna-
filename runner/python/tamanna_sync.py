#!/usr/bin/env python3
"""Optional Google Drive file sync. Disabled unless explicitly configured."""
import hashlib
import json
import os
import time
from pathlib import Path

SYNC_INTERVAL = 60
SECRET_NAMES = {
    ".env", ".env.local", ".env.production", "credentials.json",
    "token.json", "token.pickle", "service-account.json", "secrets.json",
    "id_rsa", "id_ed25519",
}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


def is_safe_upload(path):
    if path.is_symlink() or not path.is_file():
        return False
    if any(part.lower() in SECRET_NAMES or part.lower().startswith(".env.") for part in path.parts):
        return False
    return path.suffix.lower() not in SECRET_SUFFIXES


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_state(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def authenticate_drive(credentials_path):
    # Import optional dependencies only after the user explicitly enables Drive sync.
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    credentials = service_account.Credentials.from_service_account_file(
        str(credentials_path),
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def upload_file(service, path, relative_name):
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(str(path), resumable=True)
    service.files().create(
        body={"name": relative_name},
        media_body=media,
        fields="id",
    ).execute()


def sync_once():
    if os.environ.get("TAMANNA_ENABLE_DRIVE_SYNC") != "1":
        print("Drive sync disabled; set TAMANNA_ENABLE_DRIVE_SYNC=1 to opt in")
        return 0

    folder_value = os.environ.get("TAMANNA_DRIVE_SYNC_FOLDER")
    credentials_value = os.environ.get("TAMANNA_DRIVE_CREDENTIALS")
    if not folder_value or not credentials_value:
        raise RuntimeError("Set TAMANNA_DRIVE_SYNC_FOLDER and TAMANNA_DRIVE_CREDENTIALS")
    folder = Path(folder_value).expanduser().resolve()
    credentials = Path(credentials_value).expanduser().resolve()
    if not folder.is_dir():
        raise FileNotFoundError(f"Sync folder not found: {folder}")
    if not credentials.is_file() or not is_safe_upload(credentials):
        raise ValueError("Google credentials file is missing or unsafe")
    if folder == credentials or folder in credentials.parents:
        raise ValueError("Credentials file must be outside the upload folder")

    state_file = Path(os.environ.get(
        "TAMANNA_DRIVE_SYNC_STATE", str(Path.home() / ".tamanna_drive_sync_state.json")
    )).expanduser().resolve()
    if state_file.is_relative_to(folder):
        raise ValueError("Sync state file must be outside the upload folder")
    state = load_state(state_file)
    service = authenticate_drive(credentials)
    uploaded = 0

    for root, dirs, files in os.walk(folder, followlinks=False):
        root_path = Path(root)
        dirs[:] = [name for name in dirs if not (root_path / name).is_symlink()]
        for name in files:
            source = root_path / name
            if not is_safe_upload(source):
                continue
            relative = source.relative_to(folder).as_posix()
            digest = file_hash(source)
            if state.get(relative) == digest:
                continue
            upload_file(service, source, relative)
            state[relative] = digest
            uploaded += 1

    state_file.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_file.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temporary.replace(state_file)
    print(f"Drive sync completed; uploaded {uploaded} changed file(s)")
    return uploaded


def main():
    while True:
        sync_once()
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    main()
