"""Module router for Tamanna AI."""

from __future__ import annotations


async def generate_tamanna_reply_async(message: str):
    return f"Tamanna reply: {message}"


def generate_tamanna_reply(message: str):
    return f"Tamanna reply: {message}"


def reload_tamanna_modules():
    return True


__all__ = ["generate_tamanna_reply", "generate_tamanna_reply_async", "reload_tamanna_modules"]
