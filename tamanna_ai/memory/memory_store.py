"""Thread-safe JSON-backed memory store for Tamanna AI."""

from __future__ import annotations

import json
import os
import tempfile
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict


class MemoryStore:
    """Store JSON-serializable values and persist updates atomically."""

    def __init__(self, path: str | Path | None = None):
        default_path = Path(__file__).resolve().parents[2] / "data" / "tamanna_memory.json"
        configured_path = path or os.getenv("TAMANNA_MEMORY_FILE")
        self.path = Path(configured_path).expanduser() if configured_path else default_path
        self.store: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = self.path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Cannot load Tamanna memory file: {self.path}") from exc
        if not isinstance(data, dict):
            raise RuntimeError("Tamanna memory file must contain a JSON object.")
        self.store = data

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.",
            suffix=".tmp",
            dir=str(self.path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                os.chmod(temporary_name, 0o600)
                json.dump(self.store, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, self.path)
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass
        except Exception:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass
            raise

    def set(self, key: str, value: Any) -> None:
        key = str(key)
        # Validate JSON compatibility before changing in-memory state.
        json.dumps(value, ensure_ascii=False)
        with self._lock:
            existed = key in self.store
            previous = self.store.get(key)
            self.store[key] = deepcopy(value)
            try:
                self._persist()
            except Exception:
                if existed:
                    self.store[key] = previous
                else:
                    self.store.pop(key, None)
                raise

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return deepcopy(self.store.get(key, default))

    def all(self) -> Dict[str, Any]:
        with self._lock:
            return deepcopy(self.store)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key not in self.store:
                return False
            previous = self.store.pop(key)
            try:
                self._persist()
            except Exception:
                self.store[key] = previous
                raise
            return True


memory_store = MemoryStore()

__all__ = ["MemoryStore", "memory_store"]
