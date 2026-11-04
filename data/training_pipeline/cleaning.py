"""Conservative text cleaning and safety-oriented redaction helpers."""
from __future__ import annotations
import re
import unicodedata
from .privacy import redact_sensitive_data

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

def clean_text(value: str) -> tuple[str, list[str]]:
    """Normalize text and redact detectable personal data/credentials."""
    text = unicodedata.normalize("NFKC", value)
    text, flags = redact_sensitive_data(text)
    text = _CONTROL.sub(" ", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, flags
