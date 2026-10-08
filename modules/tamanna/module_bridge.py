"""Bridge for dynamic Hanna module responses."""

from __future__ import annotations


def tamanna_ai_reply(message: str):
    return f"Bridge reply: {message}"


async def tamanna_ai_reply_async(message: str):
    return f"Async bridge: {message}"


__all__ = ["tamanna_ai_reply", "tamanna_ai_reply_async"]
