"""Health checks for Tamanna AI Web Application Firewall."""
import json
from pathlib import Path
from typing import Any, Dict, Optional
from .event_logger import WAFEventLogger
from .request_inspector import RequestInspector
from .rule_engine import RuleEngine
from .waf_manager import WAFManager
def run_health_check(
    config_path: str = "waf/waf_config.json",
) -> Dict[str, Any]:
    """Check WAF configuration and component initialization."""
    result: Dict[str, Any] = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "component": "WAF",
        "status": "unhealthy",
        "checks": {},
        "request_blocking": False,
        "system_firewall_modification": False,
    }
    try:
        path = Path(config_path)
        with path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
        if not isinstance(config, dict):
            raise ValueError("Configuration root must be a JSON object.")
        result["checks"]["config_load"] = "ok"
        if config.get("project") != "Tamanna AI":
            raise ValueError("Unexpected project identity.")
        if config.get("mode") != "monitor_only":
            raise ValueError("WAF must use monitor_only mode.")
        enforcement = config.get("enforcement", {})
        if not isinstance(enforcement, dict):
            raise ValueError("Enforcement configuration must be an object.")
        if enforcement.get("block_requests", False) is not False:
            raise ValueError("Request blocking must remain disabled.")
        if enforcement.get("modify_system_firewall", False) is not False:
            raise ValueError("System firewall modification must remain disabled.")
        result["checks"]["safety_config"] = "ok"
        # Initialize components without sending or blocking a real request.
        RequestInspector(config)
        result["checks"]["request_inspector"] = "ok"
        RuleEngine(config)
        result["checks"]["rule_engine"] = "ok"
        WAFEventLogger(config)
        result["checks"]["event_logger"] = "ok"
        manager = WAFManager(config)
        manager_health = manager.health()
        if manager_health.get("status") != "ok":
            raise RuntimeError("WAF manager health check failed.")
        result["checks"]["waf_manager"] = "ok"
        result["status"] = "healthy"
    except (OSError, json.JSONDecodeError, ValueError, TypeError, RuntimeError) as exc:
        # Return a concise diagnostic without exposing file contents.
        result["status"] = "unhealthy"
        result["error"] = str(exc)
    return result
if __name__ == "__main__":
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else "waf/waf_config.json"
    print(json.dumps(
        run_health_check(config_path),
        indent=2,
        ensure_ascii=False,
    ))