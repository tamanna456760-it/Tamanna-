"""Feature toggle system."""

from __future__ import annotations

from typing import Dict


class FeatureFlags:
    def __init__(self):
        self.flags: Dict[str, bool] = {"chat": True, "scanner": True, "backup": False}

    def enable(self, name: str) -> None:
        self.flags[name] = True

    def disable(self, name: str) -> None:
        self.flags[name] = False

    def is_enabled(self, name: str) -> bool:
        return self.flags.get(name, False)


feature_flags = FeatureFlags()

__all__ = ["FeatureFlags", "feature_flags"]
