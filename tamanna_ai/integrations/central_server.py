"""Client for the Tamanna Central Server service protocol v1."""
import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.error
import urllib.request


class CentralServerError(RuntimeError):
    pass


def _canonical(method: str, path: str, timestamp: str, nonce: str, body: bytes) -> bytes:
    body_hash = hashlib.sha256(body).hexdigest()
    return "\n".join(("1", method.upper(), path, timestamp, nonce, body_hash)).encode("utf-8")


def send_report(report: dict, timeout: float = 10.0) -> dict:
    """Send a minimal service report using HMAC-SHA256 authentication.

    Configure TAMANNA_SERVER_URL, TAMANNA_SERVER_KEY_ID and
    TAMANNA_SERVER_SHARED_SECRET in the private .env file.
    """
    base_url = os.getenv("TAMANNA_SERVER_URL", "").rstrip("/")
    key_id = os.getenv("TAMANNA_SERVER_KEY_ID", "tamanna-ai")
    secret = os.getenv("TAMANNA_SERVER_SHARED_SECRET", "")
    if not base_url.startswith("https://") and not base_url.startswith("http://127.0.0.1"):
        raise CentralServerError("TAMANNA_SERVER_URL must use HTTPS (HTTP is allowed only for localhost)")
    if len(secret) < 64:
        raise CentralServerError("TAMANNA_SERVER_SHARED_SECRET must contain at least 64 characters")
    path = "/protocol/v1/report"
    body = json.dumps(report, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    timestamp = str(int(time.time()))
    nonce = secrets.token_urlsafe(24)
    signature = hmac.new(secret.encode("utf-8"), _canonical("POST", path, timestamp, nonce, body), hashlib.sha256).hexdigest()
    request = urllib.request.Request(
        base_url + path,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Tamanna-Protocol": "1",
            "X-Tamanna-Key-Id": key_id,
            "X-Tamanna-Timestamp": timestamp,
            "X-Tamanna-Nonce": nonce,
            "X-Tamanna-Signature": signature,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if response.status != 201:
                raise CentralServerError(f"Central Server returned HTTP {response.status}")
            return payload
    except urllib.error.HTTPError as exc:
        raise CentralServerError(f"Central Server rejected protocol request (HTTP {exc.code})") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise CentralServerError("Could not reach Tamanna Central Server") from exc
