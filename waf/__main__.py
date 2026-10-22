"""Command-line entry point for Tamanna AI WAF."""
import json
import sys
from .health_check import run_health_check
def main() -> int:
    """Run the WAF health check and return an exit code."""
    config_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "waf/waf_config.json"
    )
    result = run_health_check(config_path)
    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
    ))
    return 0 if result.get("status") == "healthy" else 1
if __name__ == "__main__":
    raise SystemExit(main())