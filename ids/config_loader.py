File: ids/config_loader.py

"""
Tamanna AI IDS Configuration Loader.
Project: Tamanna AI
Owner: HM INSAN ALI
Loads and validates IDS configuration without applying system changes.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
CONFIG_PATH = Path(__file__).resolve().parent / "ids_config.json"
class IDSConfigError(ValueError):
    """Raised when the IDS configuration is missing or invalid."""
def load_config(
    config_path: str | Path = CONFIG_PATH,
) -> dict[str, Any]:
    """Load and validate the IDS JSON configuration."""
    path = Path(config_path)
    try:
        with path.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except FileNotFoundError as exc:
        raise IDSConfigError(
            f"IDS configuration file not found: {path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise IDSConfigError(
            f"Invalid JSON in IDS configuration: {exc}"
        ) from exc
    if not isinstance(config, dict):
        raise IDSConfigError(
            "IDS configuration must be a JSON object."
        )
    if config.get("project") != "Tamanna AI":
        raise IDSConfigError(
            "Configuration project must be 'Tamanna AI'."
        )
    if config.get("mode") != "monitor_only":
        raise IDSConfigError(
            "Only monitor_only mode is permitted."
        )
    detection = config.get("detection")
    collection = config.get("collection")
    enforcement = config.get("enforcement")
    if not all(
        isinstance(section, dict)
        for section in (detection, collection, enforcement)
    ):
        raise IDSConfigError(
            "detection, collection, and enforcement "
            "must be JSON objects."
        )
    positive_integer_fields = (
        (detection, "failed_login_threshold"),
        (detection, "failed_login_window"),
        (detection, "request_rate_threshold"),
        (detection, "request_rate_window"),
        (collection, "max_event_size"),
        (collection, "max_in_memory_events"),
    )
    for section, field in positive_integer_fields:
        value = section.get(field)
        if type(value) is not int or value <= 0:
            raise IDSConfigError(
                f"{field} must be a positive integer."
            )
    if enforcement.get("automatic_ip_blocking") is not False:
        raise IDSConfigError(
            "automatic_ip_blocking must be false."
        )
    if enforcement.get("modify_system_firewall") is not False:
        raise IDSConfigError(
            "modify_system_firewall must be false."
        )
    if enforcement.get("manual_approval") is not True:
        raise IDSConfigError(
            "manual_approval must be true."
        )
    if collection.get("redact_secrets") is not True:
        raise IDSConfigError(
            "redact_secrets must be true."
        )
    return config
if __name__ == "__main__":
    try:
        loaded = load_config()
        print("Tamanna AI IDS configuration is valid.")
        print(f"Mode: {loaded['mode']}")
        print("Automatic IP blocking: disabled")
        print("System firewall modification: disabled")
    except IDSConfigError as exc:
        print(f"Configuration error: {exc}")
        raise SystemExit(1)