"""Configure Tamanna private server authentication settings.

Run with: python scripts/configure_private_auth.py
Writes only to the server's untracked .env file.
"""
from pathlib import Path
import os
import re
import secrets
import sys

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def set_env_value(content: str, key: str, value: str) -> str:
    line = f"{key}={value}"
    pattern = re.compile(rf"(?m)^{re.escape(key)}=.*$")
    if pattern.search(content):
        return pattern.sub(lambda _: line, content)
    return content.rstrip() + "\n" + line + "\n"


def main() -> int:
    email = input("Admin account email: ").strip().lower()
    if not EMAIL_RE.fullmatch(email):
        print("Invalid email address; no changes made.", file=sys.stderr)
        return 2

    content = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.exists() else ""
    secret_match = re.search(r"(?m)^TAMANNA_SESSION_SECRET=(.*)$", content)
    session_secret = secret_match.group(1).strip() if secret_match else ""
    if len(session_secret) < 32 or "CHANGE_ME" in session_secret:
        session_secret = secrets.token_urlsafe(48)

    values = {
        "TAMANNA_ADMIN_EMAIL": email,
        "TAMANNA_SESSION_SECRET": session_secret,
        "TAMANNA_SESSION_SECONDS": "604800",
        "TAMANNA_COOKIE_SECURE": "1",
        "TAMANNA_AUTH_DB": "data/accounts.sqlite3",
    }
    for key, value in values.items():
        content = set_env_value(content, key, value)

    ENV_FILE.write_text(content.lstrip(), encoding="utf-8")
    try:
        os.chmod(ENV_FILE, 0o600)
    except OSError as exc:
        print(f"Warning: could not set .env permissions to 600: {exc}", file=sys.stderr)
        return 1

    print("Private Tamanna authentication settings saved to .env.")
    print("Session secret generated/retained without displaying it.")
    print("Ensure .env is ignored by Git and restart the server.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
