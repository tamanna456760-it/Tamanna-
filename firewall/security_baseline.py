"""
Tamanna AI Firewall - Security Baseline
Owner: HM INSAN ALI
Read-only checks for basic firewall security settings.
Does not change operating-system firewall rules.
"""
import json
from pathlib import Path
from typing import Any
DEFAULT_CONFIG_PATH = Path(__file__).with_name("firewall_config.json")
def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load a JSON configuration without modifying the source file."""
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as file:
        config = json.load(file)
    if not isinstance(config, dict):
        raise ValueError("Firewall configuration must be a JSON object")
    return config
def check_security_baseline(
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Evaluate basic security settings.
    Returns a report with individual checks and an overall status.
    A passing baseline is not proof of complete system security.
    """
    if not isinstance(config, dict):
        raise TypeError("config must be a dictionary")
    system_firewall = config.get("system_firewall", {})
    if not isinstance(system_firewall, dict):
        system_firewall = {}
    checks = {
        "audit_only_mode": config.get("mode") == "audit_only",
        "default_deny": str(config.get("default_policy", "")).lower()
        == "deny",
        "system_rule_changes_disabled": (
            system_firewall.get("modify_system_rules") is False
        ),
        "allowed_ips_is_list": isinstance(config.get("allowed_ips"), list),
        "allowed_ports_is_list": isinstance(config.get("allowed_ports"), list),
    }
    passed = sum(checks.values())
    total = len(checks)
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "status": "PASS" if passed == total else "REVIEW_REQUIRED",
        "checks_passed": passed,
        "checks_total": total,
        "score_percent": round((passed / total) * 100, 2),
        "checks": checks,
        "system_rules_modified": False,
        "note": (
            "Configuration-only review; this does not verify live network "
            "traffic or prove that the host is secure."
        ),
    }
def main() -> int:
    try:
        config = load_config()
        report = check_security_baseline(config)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"Baseline check failed: {exc}")
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1
if __name__ == "__main__":
    raise SystemExit(main())