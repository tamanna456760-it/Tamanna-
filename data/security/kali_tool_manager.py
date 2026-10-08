"""Tool manager for security modules."""

from __future__ import annotations


class KaliToolManager:
    def discover(self):
        return {
            "ok": True,
            "tools_found": 0,
            "categories": [],
            "message": "No external security tools configured yet.",
        }


kali_tools = KaliToolManager()

__all__ = ["KaliToolManager", "kali_tools"]
