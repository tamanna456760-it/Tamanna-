"""Master Response Controller - Core AI response engine."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MessageMemory:
    """Saved replies and conversation memory."""

    def __init__(self):
        self.memory: Dict[str, str] = {}

    def add(self, key: str, reply: str) -> None:
        self.memory[key] = reply

    def get(self, key: str) -> Optional[str]:
        return self.memory.get(key)

    def search(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        for key, value in self.memory.items():
            if query_lower in key.lower():
                return value
        return None


class NLPEngine:
    """Natural language processing for intent detection and reply generation."""

    def __init__(self):
        self.grammar_rules = []
        self.semantic_vectors = {}

    def understand(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        intent = "general"

        if any(word in text_lower for word in ["hi", "hello", "hey", "হাই", "হ্যালো"]):
            intent = "greeting"
        elif any(word in text_lower for word in ["কেমন", "how are", "status", "স্ট্যাটাস"]):
            intent = "status"
        elif any(word in text_lower for word in ["নাম", "name", "who are", "your name"]):
            intent = "identity"
        elif any(word in text_lower for word in ["ধন্যবাদ", "thanks", "thank you"]):
            intent = "gratitude"
        elif any(word in text_lower for word in ["সাহায্য", "help", "assist"]):
            intent = "help_request"
        elif any(word in text_lower for word in ["scan", "স্ক্যান", "check", "find"]):
            intent = "scan"
        elif any(word in text_lower for word in ["build", "বানাও", "তৈরি", "create"]):
            intent = "build"
        elif any(word in text_lower for word in ["git", "commit", "push", "pull"]):
            intent = "git_operation"
        elif any(word in text_lower for word in ["file", "read", "write", "folder"]):
            intent = "file_operation"

        return {
            "text": text,
            "intent": intent,
            "tokens": text_lower.split(),
            "confidence": 0.85,
        }

    def generate_reply(self, intent: str, context: Dict[str, Any]) -> str:
        replies = {
            "greeting": "হাই! 🥰 আমি Tamanna AI। আপনার সাথে কথা বলতে প্রস্তুত।",
            "status": "আমি ভালো আছি। 😊 আপনার সাথে কথা বলতে প্রস্তুত।",
            "identity": "আমার নাম Tamanna AI। 🤖🥰",
            "gratitude": "আপনাকেও ধন্যবাদ। ❤️",
            "help_request": "আমি আপনাকে সাহায্য করতে প্রস্তুত। কি করতে চান?",
            "scan": "Project স্ক্যান শুরু করছি...",
            "build": "Code তৈরি করার প্রস্তুতি নিচ্ছি...",
            "git_operation": "Git অপারেশন এক্সিকিউট করছি...",
            "file_operation": "File অপারেশন প্রসেস করছি...",
            "general": f"আপনার মেসেজটি পেয়েছি। {context.get('text', 'তথ্য')}",
        }
        return replies.get(intent, replies["general"])


class ActionDetector:
    """Detect and route to appropriate actions/tools."""

    def __init__(self):
        self.actions = {}

    def register(self, name: str, handler) -> None:
        self.actions[name] = handler

    def detect(self, intent: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        action_map = {
            "scan": "code_scan",
            "build": "code_build",
            "git_operation": "git_action",
            "file_operation": "file_action",
        }
        action_name = action_map.get(intent)
        return {
            "intent": intent,
            "action": action_name,
            "should_execute": action_name is not None,
            "payload": payload,
        }


class DynamicRouter:
    """Route responses through memory, NLP and actions."""

    def __init__(self):
        self.memory = MessageMemory()
        self.nlp = NLPEngine()
        self.action_detector = ActionDetector()

    async def process(self, message: str) -> Dict[str, Any]:
        memory_reply = self.memory.search(message)
        if memory_reply:
            return {
                "ok": True,
                "source": "message_memory",
                "reply": memory_reply,
                "message": message,
            }

        understanding = self.nlp.understand(message)
        intent = understanding["intent"]
        action_info = self.action_detector.detect(intent, {"message": message})
        reply = self.nlp.generate_reply(intent, understanding)
        self.memory.add(message, reply)

        return {
            "ok": True,
            "source": "master_response_controller",
            "reply": reply,
            "message": message,
            "intent": intent,
            "understanding": understanding,
            "action": action_info,
        }


_router = DynamicRouter()


async def tamanna_master_response(message: str) -> Dict[str, Any]:
    """Main entry point for the master response system."""
    try:
        result = await _router.process(message)
        return result
    except Exception as exc:
        logger.error(f"Master response error: {exc}")
        return {
            "ok": False,
            "source": "master_response_controller",
            "reply": "দুঃখিত, Tamanna AI এখন উত্তর তৈরি করতে পারেনি।",
            "error": str(exc),
            "message": message,
        }


__all__ = [
    "tamanna_master_response",
    "MessageMemory",
    "NLPEngine",
    "ActionDetector",
    "DynamicRouter",
]
