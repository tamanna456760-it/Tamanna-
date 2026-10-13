"""Generate a health report for Tamanna AI WAF."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from .health_check import run_health_check
def generate_report(
    config_path: str = "waf/waf_config.json",
    output_path: str = "reports/waf_report.json",
) -> Dict[str, Any]:
    """Generate and save a WAF health report."""
    health = run_health_check(config_path)
    report: Dict[str, Any] = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "component": "Web Application Firewall",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "monitor_only",
        "request_blocking": False,
        "system_firewall_modification": False,
        "health": health,
    }
    destination = Path(output_path)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(destination)
        report["report_saved"] = True
        report["report_path"] = str(destination)
    except OSError:
        report["report_saved"] = False
        report["report_path"] = None
        report["error"] = "Could not save WAF report."
    return report
if __name__ == "__main__":
    import sys
    config = sys.argv[1] if len(sys.argv) > 1 else "waf/waf_config.json"
    output = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "reports/waf_report.json"
    )
    result = generate_report(config, output)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["report_saved"] or result["health"]["status"] != "healthy":
        raise SystemExit(1)