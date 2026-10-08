"""Knowledge brain for memory and reasoning."""

from __future__ import annotations

from typing import Any, Dict, List


class KnowledgeBrain:
    def __init__(self):
        self.memory: List[str] = []

    def learn(self, item: str) -> None:
        self.memory.append(item)

    def recall(self) -> List[str]:
        return self.memory

    def think(self, prompt: str) -> Dict[str, Any]:
        return {"status": "ok", "prompt": prompt, "memory_count": len(self.memory)}


knowledge_brain = KnowledgeBrain()

__all__ = ["KnowledgeBrain", "knowledge_brain"]
