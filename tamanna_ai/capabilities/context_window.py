"""Bounded context-window assembly with an approximate token estimate."""
from __future__ import annotations

from math import ceil
from typing import Sequence


def estimate_tokens(text: str) -> int:
    """Estimate tokens conservatively from UTF-8 bytes; not provider-exact."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return ceil(len(text.encode("utf-8")) / 3)


def _tail(text: str, byte_limit: int) -> str:
    return text.encode("utf-8")[-max(0, byte_limit):].decode("utf-8", errors="ignore")


def fit_context_window(
    system_prompt: str,
    context_sections: Sequence[tuple[str, str]],
    current_message: str,
    *,
    max_tokens: int = 24000,
) -> dict[str, object]:
    """Fit prioritized context into a byte budget while retaining system rules/current request."""
    if not isinstance(system_prompt, str) or not isinstance(current_message, str):
        raise TypeError("prompt and message must be strings")
    if not isinstance(max_tokens, int) or isinstance(max_tokens, bool) or max_tokens < 256:
        raise ValueError("max_tokens must be an integer of at least 256")
    budget = max_tokens * 3
    system_size = len(system_prompt.encode("utf-8"))
    if system_size + 64 > budget:
        raise ValueError("System instructions exceed the configured context window")

    current = current_message
    current_budget = budget - system_size - 128
    if len(current.encode("utf-8")) > current_budget:
        current = "[Earlier part of current message omitted]\n" + _tail(current, current_budget - 48)

    used = system_size + len(current.encode("utf-8")) + 64
    kept: dict[int, str] = {}
    truncated: list[str] = []
    # Later entries are more important (RAG, then recent history, memories, profile).
    for index in range(len(context_sections) - 1, -1, -1):
        name, content = context_sections[index]
        if not content:
            continue
        remaining = budget - used - 16
        if remaining <= 0:
            truncated.append(name)
            continue
        size = len(content.encode("utf-8"))
        if size <= remaining:
            kept[index] = content
            used += size + 16
        else:
            kept[index] = "[Earlier context omitted]\n" + _tail(content, remaining - 48)
            truncated.append(name)
            break

    parts = [system_prompt]
    parts.extend(kept[index] for index in sorted(kept))
    parts.append("Current user message:\n" + current)
    prompt = "\n\n".join(parts)
    if len(prompt.encode("utf-8")) > budget:
        raise ValueError("Unable to fit prompt within configured context window")
    return {
        "prompt": prompt,
        "estimated_tokens": estimate_tokens(prompt),
        "max_tokens": max_tokens,
        "truncated_sections": truncated,
    }


__all__ = ["estimate_tokens", "fit_context_window"]
