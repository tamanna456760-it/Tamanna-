"""Load and save Tamanna AI's local memory JSON file."""

import json
from pathlib import Path
from typing import Any

MEMORY_FILE = Path(__file__).resolve().parent / "data" / "tamanna_memory.json"


def load_memory() -> dict[str, Any]:
    """Load the memory object, creating an empty default when absent."""
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MEMORY_FILE.exists():
        return {"version": 1, "memories": []}
    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"Cannot safely read {MEMORY_FILE}") from exc
    if not isinstance(data, dict):
        raise ValueError("Memory file must contain a JSON object")
    return data


def save_memory(data: dict[str, Any]) -> None:
    """Atomically save a memory object without storing credentials."""
    if not isinstance(data, dict):
        raise TypeError("Memory data must be a dictionary")
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = MEMORY_FILE.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(MEMORY_FILE)
