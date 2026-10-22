"""
Tamanna AI — Defense Score Engine
Owner: HM INSAN ALI
Calculates a transparent score from supplied security-check results.
This is a readiness indicator, NOT a guarantee of security.
No firewall rules are changed by this module.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
REPORT_DIR = Path(__file__).with_name("reports")
REPORT_FILE = REPORT_DIR / "defense_score.json"
# Each control has a maximum weight of 100 in total.
CONTROL_WEIGHTS = {
    "policy_validation": 20,
    "audit_log_integrity": 15,
    "api_protection": 15,
    "rate_limiting": 10,
    "threat_detection": 10,
    "security_monitoring": 10,
    "backup_configured": 10,
    "authentication": 10,
}
def _normalize_checks(
    checks: dict[str, Any],
) -> tuple[dict[str, bool], list[str]]:
    normalized: dict[str, bool] = {}
    unknown: list[str] = []
    for name, result in checks.items():
        if name not in CONTROL_WEIGHTS:
            unknown.append(str(name))
            continue
        # Only an explicit boolean True counts as passed.
        normalized[name] = result is True
    return normalized, unknown
def calculate_defense_score(
    checks: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate a weighted score.
    Missing controls count as not passed. A score of 100 means all
    listed controls were reported as passing; it does not prove that
    the entire application or host is secure.
    """
    if not isinstance(checks, dict):
        raise TypeError("checks must be a dictionary")
    normalized, unknown = _normalize_checks(checks)
    total_weight = sum(CONTROL_WEIGHTS.values())
    earned_weight = 0
    controls: list[dict[str, Any]] = []
    for name, weight in CONTROL_WEIGHTS.items():
        passed = normalized.get(name, False)
        if passed:
            earned_weight += weight
        controls.append(
            {
                "name": name,
                "weight": weight,
                "passed": passed,
                "points": weight if passed else 0,
            }
        )
    score = round((earned_weight / total_weight) * 100)
    passed_count = sum(1 for item in controls if item["passed"])
    if score >= 90:
        level = "strong"
    elif score >= 75:
        level = "good"
    elif score >= 50:
        level = "needs_improvement"
    else:
        level = "weak"
    return {
        "score": score,
        "maximum_score": 100,
        "level": level,
        "passed_controls": passed_count,
        "total_controls": len(CONTROL_WEIGHTS),
        "controls": controls,
        "unknown_controls": sorted(unknown),
        "missing_controls": [
            name for name in CONTROL_WEIGHTS
            if name not in normalized
        ],
        "limitations": [
            "Scores depend on the supplied check results.",
            "A passing result is not independent proof of security.",
            "This module does not test or change host firewall rules.",
        ],
    }
def save_defense_report(
    report: dict[str, Any],
    output_path: str | Path = REPORT_FILE,
) -> Path:
    """Write a defense report to a JSON file."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report": report,
    }
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination
def build_defense_report(
    checks: dict[str, Any],
    output_path: str | Path | None = REPORT_FILE,
) -> dict[str, Any]:
    """Calculate a score and optionally save the report."""
    report = calculate_defense_score(checks)
    if output_path is not None:
        save_defense_report(report, output_path)
    return report
if __name__ == "__main__":
    # Example input only. Replace these values with real, verified
    # test results when integrating the module into Tamanna AI.
    example_checks = {
        "policy_validation": True,
        "audit_log_integrity": False,
        "api_protection": False,
        "rate_limiting": True,
        "threat_detection": True,
        "security_monitoring": True,
        "backup_configured": False,
        "authentication": False,
    }
    result = build_defense_report(example_checks)
    print("Tamanna AI — Defense Score")
    print("Score:", f'{result["score"]}/100')
    print("Level:", result["level"])
    print(
        "Passed controls:",
        f'{result["passed_controls"]}/{result["total_controls"]}',
    )
    print("Report:", REPORT_FILE)