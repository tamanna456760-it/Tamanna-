"""Load non-secret runtime settings exported from the private TI-SERVER repository.

The backend reads a local deployment file only. It never contacts GitHub, and the
browser never receives the private configuration document or filesystem path.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

# The package lives directly under the repository root.
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "private-runtime.json"
MAX_CONFIG_BYTES = 64 * 1024
_SECRET_KEY = re.compile(r"(?:secret|token|password|credential|api[_-]?key|private[_-]?key)", re.I)


class PrivateRuntimeConfigError(ValueError):
    """Raised when a present private runtime config is unsafe or malformed."""


def _safe_path(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("/") or value.startswith("//"):
        raise PrivateRuntimeConfigError(f"{field} must be an absolute local URL path.")
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise PrivateRuntimeConfigError(f"{field} must not contain a host, query, or fragment.")
    if any(part in {".", ".."} for part in parsed.path.split("/")):
        raise PrivateRuntimeConfigError(f"{field} must not contain path traversal segments.")
    return value


def _safe_base_url(value: object) -> str:
    if value in (None, ""):
        return ""
    if not isinstance(value, str) or len(value) > 2048:
        raise PrivateRuntimeConfigError("backend.base_url must be an HTTP(S) URL or empty.")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise PrivateRuntimeConfigError("backend.base_url must be an HTTP(S) URL or empty.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise PrivateRuntimeConfigError("backend.base_url must not contain credentials, query, or fragment.")
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise PrivateRuntimeConfigError("Non-local backend.base_url must use HTTPS.")
    return value.rstrip("/")


def _reject_secret_fields(value: object, location: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if _SECRET_KEY.search(str(key)):
                raise PrivateRuntimeConfigError(f"Secret-like field is not allowed in private runtime config: {location}.{key}")
            _reject_secret_fields(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_secret_fields(child, f"{location}[{index}]")


def load_private_runtime_config(path: str | Path | None = None) -> dict:
    """Load and validate the local deployment config, or return safe defaults."""
    configured_path = path or os.getenv("TAMANNA_PRIVATE_RUNTIME_CONFIG", "").strip() or DEFAULT_CONFIG_PATH
    config_path = Path(configured_path).expanduser()
    if not config_path.is_file():
        return {
            "status": "not_configured",
            "loaded": False,
            "backend": {"base_url": "", "health_path": "/health"},
            "admin": {"overview_path": "/api/admin/overview"},
            "timeouts": {"connect_seconds": 5, "read_seconds": 20},
        }
    try:
        if config_path.stat().st_size > MAX_CONFIG_BYTES:
            raise PrivateRuntimeConfigError("Private runtime config exceeds the 64 KiB limit.")
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except PrivateRuntimeConfigError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrivateRuntimeConfigError("Private runtime config could not be read as valid UTF-8 JSON.") from exc

    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise PrivateRuntimeConfigError("Unsupported private runtime config schema.")
    _reject_secret_fields(data)
    backend, admin, timeouts = data.get("backend"), data.get("admin"), data.get("timeouts")
    if not all(isinstance(section, dict) for section in (backend, admin, timeouts)):
        raise PrivateRuntimeConfigError("backend, admin, and timeouts sections are required objects.")

    connect, read = timeouts.get("connect_seconds", 5), timeouts.get("read_seconds", 20)
    if isinstance(connect, bool) or not isinstance(connect, int) or not 1 <= connect <= 30:
        raise PrivateRuntimeConfigError("timeouts.connect_seconds must be an integer from 1 to 30.")
    if isinstance(read, bool) or not isinstance(read, int) or not 1 <= read <= 120:
        raise PrivateRuntimeConfigError("timeouts.read_seconds must be an integer from 1 to 120.")

    return {
        "status": "loaded",
        "loaded": True,
        "backend": {
            "base_url": _safe_base_url(backend.get("base_url", "")),
            "health_path": _safe_path(backend.get("health_path", "/health"), "backend.health_path"),
        },
        "admin": {
            "overview_path": _safe_path(admin.get("overview_path", "/api/admin/overview"), "admin.overview_path"),
        },
        "timeouts": {"connect_seconds": connect, "read_seconds": read},
    }


def private_runtime_summary(config: dict | None) -> dict:
    """Return a safe Admin-only readiness summary without URLs or local paths."""
    value = config if isinstance(config, dict) else {}
    backend = value.get("backend") if isinstance(value.get("backend"), dict) else {}
    admin = value.get("admin") if isinstance(value.get("admin"), dict) else {}
    timeouts = value.get("timeouts") if isinstance(value.get("timeouts"), dict) else {}
    return {
        "status": value.get("status", "not_loaded"),
        "loaded": value.get("loaded") is True,
        "backend_url_configured": bool(backend.get("base_url")),
        "health_path": backend.get("health_path", "/health"),
        "admin_overview_path": admin.get("overview_path", "/api/admin/overview"),
        "timeouts": {
            "connect_seconds": timeouts.get("connect_seconds", 5),
            "read_seconds": timeouts.get("read_seconds", 20),
        },
        "secrets_exposed": False,
    }
