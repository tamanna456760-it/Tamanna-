"""Natural language action router."""

from __future__ import annotations

from typing import Any, Dict, Optional


async def route_chat_action(message: str) -> Optional[Dict[str, Any]]:
    lower = message.lower()
    if "hello" in lower or "hi" in lower:
        return {
            "ok": True,
            "intent": "greeting",
            "reply": "Hello! How can I help you today?",
        }
    if "status" in lower:
        return {
            "ok": True,
            "intent": "status",
            "reply": "Tamanna AI is online and ready.",
        }
    return None


__all__ = ["route_chat_action"]
