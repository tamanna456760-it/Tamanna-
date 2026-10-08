"""Text formatting utilities."""

from __future__ import annotations


class TextFormatter:
    def render(self, text: str, style: str = "plain") -> str:
        return f"[{style}] {text}"


text_formatter = TextFormatter()

__all__ = ["TextFormatter", "text_formatter"]
