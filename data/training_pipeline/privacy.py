"""Heuristic PII and credential redaction for training-data preparation.

This module cannot guarantee detection of unlabelled names, free-form addresses,
all government-ID formats, or sensitive meaning in arbitrary text.
"""
from __future__ import annotations
import re

_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_UAE_ID = re.compile(r"(?<!\d)784-\d{4}-\d{7}-\d(?!\d)")
_US_SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
_LABELLED_ID = re.compile(
    r"(?i)\b(?:passport(?:\s+(?:no|number))?|national\s+id(?:\s+(?:no|number))?|"
    r"identity\s+(?:card|number)|tax\s+id)\s*[:#=]\s*[A-Z0-9-]{5,20}"
)
_LABELLED_PERSON = re.compile(r"(?im)^\s*(?:full\s+)?name\s*[:=]\s*[^\r\n]{2,100}")
_LABELLED_ADDRESS = re.compile(r"(?im)^\s*(?:home\s+)?address\s*[:=]\s*[^\r\n]{5,200}")
_CARD_CANDIDATE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
_PHONE = re.compile(r"(?<!\w)\+?\d[\d(). -]{7,}\d(?!\w)")
_SECRET = re.compile(
    r"(?i)\b[A-Z0-9_]*(?:API[_-]?KEY|ACCESS[_-]?TOKEN|SECRET|PASSWORD|PRIVATE[_-]?KEY)\b"
    r"\s*[:=]\s*['\"]?[^\s,'\"]+"
)

def _luhn_valid(value: str) -> bool:
    """Validate a payment-card candidate using the Luhn checksum."""
    digits = [int(char) for char in value if char.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    checksum, parity = 0, len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0

def redact_sensitive_data(value: str) -> tuple[str, list[str]]:
    """Redact detectable PII/credentials and return category-only audit flags."""
    text, flags = value.replace("\\n", "\n"), []
    def replace(pattern: re.Pattern[str], replacement: str, flag: str) -> None:
        nonlocal text
        text, count = pattern.subn(replacement, text)
        if count and flag not in flags:
            flags.append(flag)
            if flag == "credential_redacted" and "possible_secret_redacted" not in flags:
                flags.append("possible_secret_redacted")
    replace(_SECRET, "[CREDENTIAL_REDACTED]", "credential_redacted")
    replace(_EMAIL, "[EMAIL_REDACTED]", "email_redacted")
    replace(_LABELLED_ID, "[IDENTIFIER_REDACTED]", "government_id_redacted")
    replace(_UAE_ID, "[IDENTIFIER_REDACTED]", "government_id_redacted")
    replace(_US_SSN, "[IDENTIFIER_REDACTED]", "government_id_redacted")
    replace(_LABELLED_PERSON, "Name: [PERSONAL_NAME_REDACTED]", "labelled_name_redacted")
    replace(_LABELLED_ADDRESS, "Address: [ADDRESS_REDACTED]", "labelled_address_redacted")
    def redact_card(match: re.Match[str]) -> str:
        candidate = match.group(0)
        return "[PAYMENT_CARD_REDACTED]" if _luhn_valid(candidate) else candidate
    text, count = _CARD_CANDIDATE.subn(redact_card, text)
    if count and "[PAYMENT_CARD_REDACTED]" in text:
        flags.append("payment_card_redacted")
    replace(_PHONE, "[PHONE_REDACTED]", "phone_redacted")
    return text, flags
