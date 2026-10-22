"""
Tamanna AI Firewall - Security Event Analyzer
Owner: HM INSAN ALI
Analyzes stored security events and generates summaries.
This module does not block traffic or modify system firewall rules.
"""
from collections import Counter
from datetime import datetime, timezone
from typing import Any
from firewall.security_event_store import SecurityEventStore
HIGH_RISK_SEVERITIES = {"HIGH", "CRITICAL"}
SUSPICIOUS_EVENT_KEYWORDS = (
    "failed",
    "blocked",
    "unauthorized",
    "suspicious",
    "injection",
    "malware",
    "attack",
    "denied",
)
def analyze_events(
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a summary from a list of stored security events."""
    if not isinstance(events, list):
        raise TypeError("events must be a list")
    valid_events = [
        event for event in events
        if isinstance(event, dict)
    ]
    severity_counts = Counter()
    event_type_counts = Counter()
    high_risk_count = 0
    suspicious_count = 0
    for event in valid_events:
        severity = str(event.get("severity", "UNKNOWN")).upper()
        event_type = str(event.get("event_type", "unknown"))
        severity_counts[severity] += 1
        event_type_counts[event_type] += 1
        if severity in HIGH_RISK_SEVERITIES:
            high_risk_count += 1
        searchable_text = (
            event_type + " " + severity
        ).lower()
        if any(
            keyword in searchable_text
            for keyword in SUSPICIOUS_EVENT_KEYWORDS
        ):
            suspicious_count += 1
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_events": len(valid_events),
        "severity_counts": dict(severity_counts),
        "event_type_counts": dict(event_type_counts),
        "high_risk_events": high_risk_count,
        "suspicious_events": suspicious_count,
        "system_firewall_modified": False,
        "note": (
            "Summary is based only on stored event fields. "
            "It is not proof that an attack occurred or that the "
            "system is secure."
        ),
    }
def analyze_store(
    store: SecurityEventStore | None = None,
    limit: int = 1000,
) -> dict[str, Any]:
    """Read recent events from a store and analyze them."""
    if store is None:
        store = SecurityEventStore()
    events = store.read_events(limit=limit)
    return analyze_events(events)
if __name__ == "__main__":
    import json
    report = analyze_store()
    print(json.dumps(report, indent=2, ensure_ascii=False))