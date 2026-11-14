"""Transparent rule-based action selection, not a machine-learning model."""
from typing import Any

def choose_action(options: list[dict[str, Any]], *, priority_key: str = "priority"):
    if not isinstance(options, list):
        raise TypeError("options must be a list")
    eligible = []
    for index, option in enumerate(options):
        if not isinstance(option, dict) or option.get("enabled", True) is False:
            continue
        priority = option.get(priority_key, 0)
        if isinstance(priority, bool) or not isinstance(priority, (int, float)):
            continue
        eligible.append((float(priority), -index, option))
    return max(eligible, key=lambda row: (row[0], row[1]))[2] if eligible else None

__all__ = ["choose_action"]
