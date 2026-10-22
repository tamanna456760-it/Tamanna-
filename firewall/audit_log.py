
"""
Tamanna AI — Advanced Security Audit Logger
Owner: HM INSAN ALI

Structured security event logging with:
- UTC timestamps
- Event validation
- Secret redaction
- JSON Lines output
- Basic log integrity chaining

Important:
Hash chaining can help detect changes, but it does not prevent
an administrator from rewriting the entire log and chain.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOG_FILE = BASE_DIR / "firewall_audit.jsonl"

MAX_EVENT_LENGTH = 120
MAX_DETAILS_DEPTH = 6
MAX_STRING_LENGTH = 2000

SECRET_KEY_PATTERN = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|authorization|"
    r"cookie|private[_-]?key|credential)",
    re.IGNORECASE,
)

SENSITIVE_TEXT_PATTERN = re.compile(
    r"(?i)\b(bearer\s+)[A-Za-z0-9._~+/=-]+"
)


def _redact(value: Any, depth: int = 0) -> Any:
    """Sanitize audit details and redact likely secret values."""
    if depth > MAX_DETAILS_DEPTH:
        return "[MAX_DEPTH_REACHED]"

    if isinstance(value, dict):
        result = {}

        for key, item in list(value.items())[:100]:
            safe_key = str(key)[:100]

            if SECRET_KEY_PATTERN.search(safe_key):
                result[safe_key] = "[REDACTED]"
            else:
                result[safe_key] = _redact(item, depth + 1)

        return result

    if isinstance(value, (list, tuple)):
        return [
            _redact(item, depth + 1)
            for item in value[:100]
        ]

    if isinstance(value, str):
        safe_value = SENSITIVE_TEXT_PATTERN.sub(
            r"\1[REDACTED]",
            value[:MAX_STRING_LENGTH],
        )
        return safe_value

    if value is None or isinstance(value, (bool, int, float)):
        return value

    return f"[UNSUPPORTED_TYPE:{type(value).__name__}]"


def _canonical_json(data: dict[str, Any]) -> str:
    """Create deterministic JSON for integrity hashing."""
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _previous_hash(log_file: Path) -> str:
    """Return the last record hash, or the genesis value."""
    if not log_file.exists():
        return "GENESIS"

    try:
        with log_file.open("rb") as file:
            lines = file.readlines()

        if not lines:
            return "GENESIS"

        previous = json.loads(lines[-1].decode("utf-8"))
        return str(previous.get("record_hash", "INVALID_CHAIN"))

    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "INVALID_CHAIN"


def record_event(
    event: str,
    details: dict[str, Any] | None = None,
    log_file: Path | str | None = None,
) -> dict[str, Any]:
    """
    Append one sanitized event to the audit log.

    For security-sensitive deployments, configure filesystem permissions
    and ship a separate copy to protected remote or immutable storage.
    """
    if not isinstance(event, str) or not event.strip():
        raise ValueError("Event must be a non-empty string.")

    destination = Path(log_file) if log_file else DEFAULT_LOG_FILE
    destination.parent.mkdir(parents=True, exist_ok=True)

    safe_details = _redact(
        details if isinstance(details, dict) else {}
    )

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event.strip()[:MAX_EVENT_LENGTH],
        "details": safe_details,
        "previous_hash": _previous_hash(destination),
    }

    record["record_hash"] = hashlib.sha256(
        _canonical_json(record).encode("utf-8")
    ).hexdigest()

    # Restrict permissions on newly created log files where supported.
    file_descriptor = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT | os.O_APPEND,
        0o600,
    )

    try:
        with os.fdopen(file_descriptor, "a", encoding="utf-8") as file:
            file.write(
                json.dumps(record, ensure_ascii=False, allow_nan=False)
                + "\n"
            )
    except Exception:
        raise

    return record


def verify_log(log_file: Path | str | None = None) -> dict[str, Any]:
    """Check JSONL records and their sequential hash chain."""
    destination = Path(log_file) if log_file else DEFAULT_LOG_FILE

    if not destination.exists():
        return {
            "ok": True,
            "records_checked": 0,
            "message": "Audit log does not exist yet.",
        }

    previous_hash = "GENESIS"
    records_checked = 0

    try:
        with destination.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                record = json.loads(line)
                stored_hash = record.pop("record_hash", None)

                if record.get("previous_hash") != previous_hash:
                    return {
                        "ok": False,
                        "line": line_number,
                        "message": "Previous hash mismatch.",
                    }

                calculated_hash = hashlib.sha256(
                    _canonical_json(record).encode("utf-8")
                ).hexdigest()

                if stored_hash != calculated_hash:
                    return {
                        "ok": False,
                        "line": line_number,
                        "message": "Record hash mismatch.",
                    }

                previous_hash = stored_hash
                records_checked += 1

    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {
            "ok": False,
            "records_checked": records_checked,
            "message": "Unable to parse or read audit log.",
        }

    return {
        "ok": True,
        "records_checked": records_checked,
        "message": "Audit log hash chain verified.",
    }


if __name__ == "__main__":
    event = record_event(
        "audit_logger_self_test",
        {"module": "Tamanna AI Firewall", "test": True},
    )

    print(json.dumps({
        "event_recorded": True,
        "record_hash": event["record_hash"],
        "verification": verify_log(),
    }, indent=2, ensure_ascii=False))
