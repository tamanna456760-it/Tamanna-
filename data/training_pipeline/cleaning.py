"""Conservative text cleaning and safety-oriented redaction helpers."""

from __future__ import annotations

import re
import unicodedata

_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d(). -]{7,}\d)(?!\w)")
_SECRET = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"]?[^\s,'\"]+"
)
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(value: str) -> tuple[str, list[str]]:
    """Normalize text and redact common personal data/credentials; return audit flags."""
    flags: list[str] = []
    text = unicodedata.normalize("NFKC", value)
    text, count = _SECRET.subn(r"\1=[REDACTED]", text)
    if count:
        flags.append("possible_secret_redacted")
    text, count = _EMAIL.subn("[EMAIL_REDACTED]", text)
    if count:
        flags.append("email_redacted")
    text, count = _PHONE.subn("[PHONE_REDACTED]", text)
    if count:
        flags.append("phone_redacted")
    text = _CONTROL.sub(" ", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, flags
