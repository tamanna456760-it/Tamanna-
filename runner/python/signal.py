
"""Tamanna AI intrusion-signal helpers.

This module classifies supplied event text.
It does not modify system settings or block connections.
"""

SUSPICIOUS_MARKERS = (
    "unauthorized",
    "failed_login",
    "strange_ip",
    "file_change",
)


def detect_intrusion(event: str) -> bool:
    """Detect known suspicious markers in an event."""
    normalized = str(event).lower()
    return any(marker in normalized for marker in SUSPICIOUS_MARKERS)


def tamanna_defense(event: str) -> str:
    """Return a human-readable security status."""
    if detect_intrusion(event):
        return "Tamanna: সতর্ক! সন্দেহজনক কার্যকলাপ ধরা পড়েছে."
    return "Tamanna: সব ঠিক আছে, সিস্টেম শান্ত."


if __name__ == "__main__":
    print(tamanna_defense("failed_login from unknown IP"))
