"""Read-only GitHub backup snapshot utility.

This module deliberately has no automatic restore or repository write capability.
Provide TAMANNA_GITHUB_TOKEN through the private server environment when needed.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import requests

REPO_OWNER = "tamanna456760-it"
REPO_NAME = "Tamanna-"
API_ROOT = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
BACKUP_FILE = Path(os.getenv("TAMANNA_BACKUP_FILE", "ai_backup_db.json"))
REQUEST_TIMEOUT = (5, 20)
MAX_FILE_BYTES = 2 * 1024 * 1024


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("TAMANNA_GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_json(path: str | Path = BACKUP_FILE) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_json(path: str | Path, data: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def get_repo_files() -> list[dict[str, Any]]:
    response = requests.get(
        f"{API_ROOT}/git/trees/main?recursive=1",
        headers=_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("truncated"):
        raise RuntimeError("Git tree response was truncated; refusing incomplete backup.")
    return [
        item for item in payload.get("tree", [])
        if item.get("type") == "blob"
        and isinstance(item.get("size"), int)
        and item["size"] <= MAX_FILE_BYTES
    ]


def get_file_content(file: dict[str, Any]) -> str | None:
    url = file.get("url")
    if not isinstance(url, str) or not url.startswith("https://api.github.com/repos/"):
        raise ValueError("Invalid GitHub API blob URL.")
    response = requests.get(url, headers=_headers(), timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if payload.get("encoding") != "base64" or not isinstance(payload.get("content"), str):
        return None
    import base64
    raw = base64.b64decode(payload["content"], validate=False)
    if len(raw) > MAX_FILE_BYTES:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def create_dual_backup(path: str, content: str, backup_db: dict[str, Any]) -> None:
    backup_db[path] = {
        "content": content,
        "sha256": get_hash(content),
    }


def restore_file(path: str, backup_db: dict[str, Any]) -> str | None:
    """Return a previously captured snapshot; never writes to GitHub or disk."""
    entry = backup_db.get(path)
    if not isinstance(entry, dict):
        return None
    content = entry.get("content")
    digest = entry.get("sha256")
    if not isinstance(content, str) or digest != get_hash(content):
        return None
    return content


def detect_attack(content: str) -> bool:
    """Heuristic indicator only; not a malware verdict."""
    indicators = ("rm -rf", "eval(", "os.system(", "subprocess.Popen")
    lowered = content.lower()
    return any(indicator.lower() in lowered for indicator in indicators)


def ai_backup_network() -> dict[str, Any]:
    """Create a read-only text snapshot of eligible files from the default branch."""
    backup_db = load_json()
    scanned = 0
    skipped = 0
    indicators: list[str] = []

    for item in get_repo_files():
        path = item.get("path")
        if not isinstance(path, str):
            skipped += 1
            continue
        # Never snapshot likely secrets, credentials, local environments, or binaries.
        parts = Path(path).parts
        if any(part in {".git", ".venv", "venv", "node_modules", "__pycache__"} for part in parts):
            skipped += 1
            continue
        if Path(path).name.lower() in {".env", ".env.local", "id_rsa", "id_ed25519"}:
            skipped += 1
            continue
        content = get_file_content(item)
        if content is None:
            skipped += 1
            continue
        create_dual_backup(path, content, backup_db)
        scanned += 1
        if detect_attack(content):
            indicators.append(path)

    save_json(BACKUP_FILE, backup_db)
    return {
        "status": "completed",
        "mode": "read_only",
        "files_snapshotted": scanned,
        "files_skipped": skipped,
        "heuristic_indicators": indicators,
        "automatic_restore": False,
        "github_write_enabled": False,
    }


if __name__ == "__main__":
    print(json.dumps(ai_backup_network(), ensure_ascii=False, indent=2))
