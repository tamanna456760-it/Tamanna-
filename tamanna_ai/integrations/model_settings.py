"""Persisted, secret-free local model selection for Tamanna AI."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL_SETTINGS_PATH = Path(
    os.getenv("TAMANNA_MODEL_SETTINGS_PATH", str(ROOT / "data" / "model_settings.json"))
)
_MODEL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$")


def get_selected_model() -> str | None:
    """Return the user-selected local model, if a valid setting exists."""
    try:
        payload = json.loads(MODEL_SETTINGS_PATH.read_text(encoding="utf-8"))
        model = payload.get("selected_model") if isinstance(payload, dict) else None
        return model if isinstance(model, str) and _MODEL_NAME.fullmatch(model) else None
    except (OSError, ValueError, TypeError):
        return None


def set_selected_model(model: str) -> str:
    """Atomically persist a validated model name; no credentials are stored."""
    if not isinstance(model, str) or not _MODEL_NAME.fullmatch(model):
        raise ValueError("Invalid local model name.")
    MODEL_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = MODEL_SETTINGS_PATH.with_suffix(".tmp")
    temporary.write_text(
        json.dumps({"selected_model": model}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, MODEL_SETTINGS_PATH)
    return model


__all__ = ["get_selected_model", "set_selected_model"]
