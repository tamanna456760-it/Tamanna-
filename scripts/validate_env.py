#!/usr/bin/env python3
"""Validate private Tamanna AI environment configuration without printing secrets."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def validate_env(env_file: Path, strict: bool = False) -> dict:
    if env_file.is_file():
        load_dotenv(env_file, override=False)
        file_values = dotenv_values(env_file)
    else:
        file_values = {}

    def value(name: str) -> str:
        return str(os.getenv(name) or file_values.get(name) or "").strip()

    checks = {
        "session_secret": len(value("TAMANNA_SESSION_SECRET")) >= 32,
        "gemini_api_key": bool(value("TAMANNA_MODEL_API_KEY") or value("GEMINI_API_KEY")),
        "database_url": True,  # SQLite is the supported built-in fallback.
        "cors_origins": bool(value("TAMANNA_CORS_ORIGINS")),
    }
    missing = [name for name, ok in checks.items() if not ok]
    warnings = []
    if not checks["gemini_api_key"]:
        warnings.append("Gemini chat is unavailable until GEMINI_API_KEY or TAMANNA_MODEL_API_KEY is set.")
    if not checks["session_secret"]:
        warnings.append("Signup/login is unavailable until TAMANNA_SESSION_SECRET is set to at least 32 characters.")
    if not checks["database_url"]:
        warnings.append("Set TAMANNA_DATABASE_URL or use the built-in SQLite default.")
    if not checks["cors_origins"]:
        warnings.append("Set TAMANNA_CORS_ORIGINS to the exact trusted frontend origins.")

    blocking = ["session_secret", "gemini_api_key"] if strict else []
    failed = any(not checks[name] for name in blocking)
    return {
        "status": "FAIL" if failed else ("WARNING" if missing else "PASS"),
        "env_file_exists": env_file.is_file(),
        "checks": checks,
        "missing": missing,
        "warnings": warnings,
        "secrets_printed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--strict", action="store_true",
                        help="Require both a valid session secret and Gemini API key.")
    args = parser.parse_args()
    report = validate_env(args.env_file, strict=args.strict)
    print(json.dumps(report, indent=2))
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
