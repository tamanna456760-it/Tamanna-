"""Safe, read-only Ethical Hacking audit for Tamanna AI.

Only inspects repository configuration and known safety guards. It does not
connect to hosts, scan ports, execute scripts, exploit services, or remediate.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def _check(name: str, ok: bool, detail: str) -> dict[str, str]:
    return {
        "name": name,
        "status": "PASS" if ok else "REVIEW_REQUIRED",
        "detail": detail,
    }


def run_ethical_audit(root: str | Path) -> dict[str, Any]:
    """Inspect the checked-out project using fixed, read-only file paths."""
    base = Path(root).resolve()
    checks: list[dict[str, str]] = []

    config_path = base / "endpoint_security" / "endpoint_config.json"
    try:
        import json
        from endpoint_security.config_validator import validate_config
        from endpoint_security.policy_checker import check_policy

        config = json.loads(config_path.read_text(encoding="utf-8"))
        errors = validate_config(config)
        policy = check_policy(config)
        checks.append(_check(
            "endpoint_security_config",
            not errors,
            "Monitor-only security configuration is valid."
            if not errors else "; ".join(errors),
        ))
        checks.append(_check(
            "endpoint_security_policy",
            policy.get("valid") is True,
            "Destructive enforcement remains disabled."
            if policy.get("valid") else "; ".join(policy.get("violations", [])),
        ))
    except (OSError, ValueError, TypeError, ImportError) as exc:
        reason = f"Could not validate security configuration ({type(exc).__name__})."
        checks.append(_check("endpoint_security_config", False, reason))
        checks.append(_check("endpoint_security_policy", False, reason))

    guard_path = base / "scripts" / "check_legacy_shell_safety.py"
    guard_ok = False
    guarded_count = 0
    try:
        tree = ast.parse(guard_path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "QUARANTINED"
                for target in node.targets
            ):
                entries = ast.literal_eval(node.value)
                if isinstance(entries, tuple) and all(isinstance(x, str) for x in entries):
                    guarded_count = len(entries)
                    guard_ok = guarded_count > 0 and all(
                        "SAFETY HOLD" in (base / entry).read_text(encoding="utf-8")
                        and "exit 2" in (base / entry).read_text(encoding="utf-8")
                        for entry in entries
                    )
                break
    except (OSError, SyntaxError, ValueError, TypeError):
        guard_ok = False
    checks.append(_check(
        "legacy_script_safety_guards",
        guard_ok,
        f"{guarded_count} legacy scripts have fail-closed guards."
        if guard_ok else "One or more legacy safety guards are missing or altered.",
    ))

    gitignore = base / ".gitignore"
    try:
        ignored = {
            line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        env_ok = ".env" in ignored and ".env.*" in ignored
    except OSError:
        env_ok = False
    checks.append(_check(
        "private_environment_files",
        env_ok,
        ".env and .env.* are excluded from Git."
        if env_ok else "Review .gitignore; private environment files must be excluded.",
    ))

    middleware = base / "tamanna_ai" / "security" / "request_limits.py"
    checks.append(_check(
        "request_security_middleware",
        middleware.is_file(),
        "Request-size and security-header middleware source exists."
        if middleware.is_file() else "Request security middleware source is missing.",
    ))

    passed = sum(item["status"] == "PASS" for item in checks)
    failed = len(checks) - passed
    return {
        "project": "Tamanna AI",
        "mode": "read_only",
        "summary": {
            "total": len(checks),
            "passed": passed,
            "review_required": failed,
            "status": "PASS" if failed == 0 else "REVIEW_REQUIRED",
        },
        "checks": checks,
        "limitations": [
            "No network requests, port scans, exploit attempts, or host changes were performed.",
            "This source/configuration audit does not certify the live website or VPS.",
            "A passing result is not a penetration-test certification.",
        ],
    }
