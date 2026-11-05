"""Runtime feature flags for Tamanna AI.

Flags are process-local defaults, not a substitute for authorization.
Sensitive capabilities must still enforce access control in their API routes.
"""

from __future__ import annotations

from threading import RLock
from typing import Dict


class FeatureFlags:
    def __init__(self):
        self._lock = RLock()
        self.flags: Dict[str, bool] = {
            "chat": True,
            "memory": True,
            "personalization": True,
            "scanner": True,
            "backup": False,
            "web_search": False,
            "file_manager": False,
            "code_analysis": False,
            "voice": False,
        }

    def enable(self, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Feature name is required")
        with self._lock:
            self.flags[name.strip()] = True

    def disable(self, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Feature name is required")
        with self._lock:
            self.flags[name.strip()] = False

    def is_enabled(self, name: str) -> bool:
        with self._lock:
            return self.flags.get(name, False)

    def snapshot(self) -> Dict[str, bool]:
        with self._lock:
            return dict(self.flags)


feature_flags = FeatureFlags()

__all__ = ["FeatureFlags", "feature_flags"]
