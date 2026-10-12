"""
Tamanna AI Firewall - Doctor
Owner: HM INSAN ALI
Read-only diagnostic checks. Does not change system firewall rules.
"""
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
REQUIRED_FILES = (
    "firewall_config.json",
    "firewall_manager.py",
    "access_control.py",
    "audit_log.py",
    "security_status.py",
)
REQUIRED_MODULES = (
    "firewall.firewall_manager",
    "firewall.access_control",
    "firewall.audit_log",
    "firewall.security_status",
)
def run_diagnostics(base_dir=None):
    """Run basic, read-only project diagnostics."""
    root = Path(base_dir) if base_dir else Path(__file__).parent
    checks = []
    errors = []
    for relative_path in REQUIRED_FILES:
        exists = (root / relative_path).is_file()
        checks.append({
            "name": f"file:{relative_path}",
            "passed": exists,
        })
        if not exists:
            errors.append(f"Missing required file: {relative_path}")
    config_path = root / "firewall_config.json"
    config = None
    if config_path.is_file():
        try:
            with config_path.open("r", encoding="utf-8") as file:
                config = json.load(file)
            config_ok = (
                isinstance(config, dict)
                and config.get("mode")
                in {"audit_only", "monitor", "enforce"}
                and isinstance(config.get("allowed_ips", []), list)
                and isinstance(config.get("allowed_ports", []), list)
            )
            checks.append({
                "name": "config:basic_validation",
                "passed": config_ok,
            })
            if not config_ok:
                errors.append("Firewall configuration failed basic validation.")
        except (OSError, json.JSONDecodeError) as exc:
            checks.append({
                "name": "config:json_read",
                "passed": False,
            })
            errors.append(f"Unable to read firewall configuration: {exc}")
    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
            passed = True
        except Exception as exc:
            passed = False
            errors.append(
                f"Import failed for {module_name}: "
                f"{type(exc).__name__}: {exc}"
            )
        checks.append({
            "name": f"import:{module_name}",
            "passed": passed,
        })
    failed_count = sum(not item["passed"] for item in checks)
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "status": "OK" if failed_count == 0 else "ISSUES_FOUND",
        "checks_passed": len(checks) - failed_count,
        "checks_failed": failed_count,
        "checks": checks,
        "errors": errors,
        "system_firewall_modified": False,
        "note": (
            "Diagnostics check project files, basic configuration, and imports. "
            "They do not test live traffic filtering or operating-system rules."
        ),
    }
if __name__ == "__main__":
    result = run_diagnostics()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "OK" else 1)