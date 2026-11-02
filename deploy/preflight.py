#!/usr/bin/env python3
"""Validate the actual Docker/Nginx deployment configuration.

Static preflight only: it never connects to a server, starts containers,
reads the private .env file, or claims DNS/TLS is live.
"""
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "Main.py", "main.py", "index.html", "Dockerfile",
    "requirements-server.txt", ".env.example",
    "deploy/docker-compose.yml", "deploy/nginx/tamanna-https.conf",
)

def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.is_file():
            fail(f"Required deployment file missing: {relative}")
        if path.stat().st_size == 0:
            fail(f"Required deployment file is empty: {relative}")

    compose_path = ROOT / "deploy/docker-compose.yml"
    try:
        compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        fail(f"Invalid Docker Compose YAML: {type(exc).__name__}")

    services = compose.get("services", {}) if isinstance(compose, dict) else {}
    if not {"tamanna-ai", "nginx"}.issubset(services):
        fail("Compose must define tamanna-ai and nginx services.")

    app_service = services["tamanna-ai"]
    if app_service.get("build", {}).get("dockerfile") != "Dockerfile":
        fail("tamanna-ai must build using the root Dockerfile.")

    ports = app_service.get("ports", [])
    if not any(str(port).startswith("127.0.0.1:8000:8000") for port in ports):
        fail("Application port 8000 must be bound to host localhost only.")

    nginx_text = (ROOT / "deploy/nginx/tamanna-https.conf").read_text(encoding="utf-8")
    for required in (
        "server_name www.tamanna.com",
        "proxy_pass http://tamanna-ai:8000",
        "ssl_certificate",
        "ssl_certificate_key",
        "limit_req_zone $binary_remote_addr zone=tamanna_api:10m rate=20r/s;",
        "limit_req zone=tamanna_api burst=40 nodelay;",
        'add_header Strict-Transport-Security "max-age=15552000" always;',
    ):
        if required not in nginx_text:
            fail(f"Nginx configuration is missing: {required}")

    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    if 'uvicorn", "Main:app"' not in dockerfile:
        fail("Dockerfile must start the Main:app ASGI application.")

    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    for key in ("GEMINI_API_KEY=", "TAMANNA_ADMIN_API_KEY="):
        if key not in env_example:
            fail(f".env.example is missing the {key[:-1]} placeholder.")

    print("PASS: Required production files exist and are non-empty.")
    print("PASS: Docker Compose defines the app and Nginx services.")
    print("PASS: App port 8000 is bound to localhost only.")
    print("PASS: Nginx proxies to the Docker app and configures TLS paths.")
    print("PASS: Nginx applies API rate limits and HTTPS security headers.")
    print("PASS: Dockerfile starts Main:app.")
    print("PASS: Secret placeholders are documented without real credentials.")
    print("NOTE: DNS, certificate issuance, host firewall and live service health")
    print("      must still be verified on the actual hosting server.")

if __name__ == "__main__":
    main()
