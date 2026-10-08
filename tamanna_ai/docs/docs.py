"""Simple document manager."""

from __future__ import annotations

from typing import Dict


class DocumentManager:
    def __init__(self):
        self.documents: Dict[str, str] = {}

    def add(self, name: str, content: str) -> None:
        self.documents[name] = content

    def list(self):
        return list(self.documents.keys())

    def get(self, name: str) -> str:
        return self.documents.get(name, "")


document_manager = DocumentManager()

__all__ = ["DocumentManager", "document_manager"]
