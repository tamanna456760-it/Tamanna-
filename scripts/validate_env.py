#!/usr/bin/env python3
"""Validate private Tamanna AI environment configuration without printing secrets."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import dotenv_values, load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def validate_env(env_file: Path, strict: bool = False) -> dict:
    if env_file.is_file():
        load_dotenv(env_file, override=False)
        file_values = dotenv_values(env_file)
    else:
        file_values = {}

    def value(name: str, default: str = "") -> str:
        return str(os.getenv(name) or file_values.get(name) or default).strip()

    provider = value("TAMANNA_MODEL_PROVIDER", "ollama").lower()
    environment = value("TAMANNA_ENV", "production").lower()
    ollama_url = value("TAMANNA_OLLAMA_URL", "http://127.0.0.1:11434")
    ollama_model = value("TAMANNA_OLLAMA_MODEL", "qwen2.5:7b")
    parsed_ollama_url = urlparse(ollama_url)
    ollama_configured = (
        parsed_ollama_url.scheme in {"http", "https"}
        and bool(parsed_ollama_url.netloc)
        and bool(ollama_model)
        and len(ollama_model) <= 200
    )
    provider_configured = (
        provider == "ollama" and ollama_configured
    ) or (
        provider == "mock" and environment == "test"
    )

    checks = {
        "session_secret": len(value("TAMANNA_SESSION_SECRET")) >= 32,
        "model_provider": provider_configured,
        "database_url": bool(value("TAMANNA_DATABASE_URL", "sqlite:///data/tamanna.sqlite3")),
        "cors_origins": bool(value("TAMANNA_CORS_ORIGINS")),
    }
    missing = [name for name, ok in checks.items() if not ok]
    warnings = []
    if not checks["session_secret"]:
        warnings.append("Set TAMANNA_SESSION_SECRET to a unique value of at least 32 characters.")
    if not checks["model_provider"]:
        warnings.append(
            "Use TAMANNA_MODEL_PROVIDER=ollama with a valid local Ollama URL/model; "
            "mock is allowed only when TAMANNA_ENV=test."
        )
    if not checks["database_url"]:
        warnings.append("Set TAMANNA_DATABASE_URL or use the built-in SQLite default.")
    if not checks["cors_origins"]:
        warnings.append("Set TAMANNA_CORS_ORIGINS to the exact trusted frontend origins.")

    blocking = ["session_secret", "model_provider", "database_url", "cors_origins"] if strict else []
    failed = any(not checks[name] for name in blocking)
    return {
        "status": "FAIL" if failed else ("WARNING" if missing else "PASS"),
        "env_file_exists": env_file.is_file(),
        "checks": checks,
        "missing": missing,
        "warnings": warnings,
        "provider": provider,
        "secrets_printed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require a strong session secret, supported local model provider, database URL, and trusted CORS origins.",
    )
    args = parser.parse_args()
    report = validate_env(args.env_file, strict=args.strict)
    print(json.dumps(report, indent=2))
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
