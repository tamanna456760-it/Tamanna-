"""
Tamanna AI Firewall - Security Baseline Report
Owner: HM INSAN ALI
Generates a JSON report from read-only configuration checks.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from firewall.security_baseline import (
    check_security_baseline,
    load_config,
)
FIREWALL_DIR = Path(__file__).resolve().parent
DEFAULT_REPORT_PATH = FIREWALL_DIR / "reports" / "security_baseline.json"
def generate_report(
    config_path: str | Path = FIREWALL_DIR / "firewall_config.json",
    report_path: str | Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    """Check the configuration and save the results as JSON."""
    config = load_config(config_path)
    baseline = check_security_baseline(config)
    report = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baseline": baseline,
    }
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Write atomically to avoid leaving a partially written report.
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return report
def main() -> int:
    try:
        report = generate_report()
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"Could not generate security baseline report: {exc}")
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport saved to: {DEFAULT_REPORT_PATH}")
    return 0 if report["baseline"]["status"] == "PASS" else 1
if __name__ == "__main__":
    raise SystemExit(main())