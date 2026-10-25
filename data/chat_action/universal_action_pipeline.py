
"""Safe universal chat-action pipeline for Tamanna AI.

This module classifies messages and returns suggestions.
It does not execute shell commands, modify files, or push to GitHub.
"""

from __future__ import annotations

from typing import Any


def handle(message: str) -> dict[str, Any]:
    """Classify a chat message and return a structured response."""
    text = str(message or "").strip()
    lowered = text.lower()

    if not text:
        return {
            "ok": False,
            "intent": "empty",
            "reply": "দয়া করে একটি বার্তা লিখুন।",
        }

    if any(word in lowered for word in ("hello", "hi", "হ্যালো", "হাই")):
        intent = "greeting"
        reply = "হ্যালো! আমি Tamanna AI। কীভাবে সাহায্য করতে পারি?"

    elif any(word in lowered for word in ("status", "স্ট্যাটাস", "অবস্থা")):
        intent = "status"
        reply = "Tamanna AI chat-action pipeline সাড়া দিচ্ছে।"

    elif any(word in lowered for word in ("help", "সাহায্য")):
        intent = "help"
        reply = (
            "আমি বার্তা শ্রেণিবদ্ধ করতে, সাধারণ তথ্য দিতে এবং "
            "পরবর্তী কাজের পরামর্শ দিতে পারি।"
        )

    elif any(word in lowered for word in ("scan", "স্ক্যান")):
        intent = "scan_request"
        reply = (
            "স্ক্যানের অনুরোধ শনাক্ত হয়েছে। "
            "প্রকৃত স্ক্যান চালাতে অনুমোদিত scanner integration দরকার।"
        )

    elif any(word in lowered for word in ("build", "বানাও", "তৈরি করো")):
        intent = "build_request"
        reply = (
            "Build-এর অনুরোধ শনাক্ত হয়েছে। "
            "কোড তৈরি বা পরিবর্তনের আগে প্রয়োজনীয় ফাইল ও অনুমতি যাচাই করতে হবে।"
        )

    elif any(word in lowered for word in ("git push", "push করো", "commit করো")):
        intent = "git_operation_request"
        reply = (
            "Git অপারেশনের অনুরোধ শনাক্ত হয়েছে। "
            "এই pipeline নিজে থেকে commit বা push করে না।"
        )

    else:
        intent = "general"
        reply = (
            "আপনার বার্তা পেয়েছি। আরও নির্দিষ্টভাবে বলুন "
            "কোন কাজটি করতে চান।"
        )

    return {
        "ok": True,
        "intent": intent,
        "message": text,
        "reply": reply,
        "executed": False,
    }


__all__ = ["handle"]
