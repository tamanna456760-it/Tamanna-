"""Validate the Tamanna AI IDS configuration and runtime health."""
import json
import sys
from ids.config_loader import load_config
from ids.health_check import run_health_check
from ids.ids_manager import IDSManager
def main():
    """Run configuration and health checks."""
    print("Tamanna AI IDS - Project Validation")
    print("=" * 40)
    try:
        config = load_config()
        print("[PASS] Configuration loaded")
        print(f"[INFO] Project: {config.get('project', 'Tamanna AI')}")
        print(f"[INFO] Mode: {config.get('mode', 'monitor_only')}")
        if config.get("mode") != "monitor_only":
            print("[FAIL] IDS must use monitor_only mode")
            return 1
        enforcement = config.get("enforcement", {})
        if enforcement.get("automatic_ip_blocking") is not False:
            print("[FAIL] Automatic IP blocking must be disabled")
            return 1
        if enforcement.get("modify_system_firewall") is not False:
            print("[FAIL] System firewall modification must be disabled")
            return 1
        print("[PASS] Monitor-only safety settings verified")
        manager = IDSManager(mode="monitor_only")
        health = run_health_check(manager)
        print("[INFO] Health check:")
        print(json.dumps(health, indent=2, ensure_ascii=False))
        if health.get("status") not in ("healthy", "ok"):
            print("[FAIL] Health check did not report healthy status")
            return 1
        print("[PASS] Project validation completed")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"[FAIL] Validation error: {exc}", file=sys.stderr)
        return 1
if __name__ == "__main__":
    raise SystemExit(main())