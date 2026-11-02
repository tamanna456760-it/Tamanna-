#!/usr/bin/env python3
"""Read-only preflight checks for Tamanna AI self-hosted deployment."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "index.html",
    "Main.py",
    "main.py",
    "Dockerfile",
    "requirements-server.txt",
    ".dockerignore",
    "CNAME",
    ".github/workflows/deploy.yml",
    ".github/workflows/pages.yml",
    "deploy/docker-compose.yml",
    "deploy/nginx/tamanna-https.conf",
    "deploy/deploy.sh",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(relative: str) -> str:
    try:
        return (ROOT / relative).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        fail(f"Cannot read {relative}: {type(exc).__name__}")
        raise AssertionError("unreachable")


def main() -> None:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            fail(f"Required deployment file missing: {relative}")

    cname = read_text("CNAME").strip().lower()
    if cname != "www.tamanna.com":
        fail("CNAME must contain exactly www.tamanna.com")

    dockerignore = set(read_text(".dockerignore").splitlines())
    for pattern in (".env", ".env.*"):
        if pattern not in dockerignore:
            fail(f".dockerignore must exclude {pattern!r}")

    compose = read_text("deploy/docker-compose.yml")
    required_compose_markers = (
        "127.0.0.1:8000:8000",
        "no-new-privileges:true",
        "condition: service_healthy",
        "/health",
        "tamanna-ai-data:/app/data",
        "80:80",
        "443:443",
        "name: tamanna-ai-data",
    )
    if compose.count("\nvolumes:\n") != 1:
        fail("Docker Compose must declare exactly one top-level volumes section")
    for marker in required_compose_markers:
        if marker not in compose:
            fail(f"Docker Compose is missing required setting: {marker}")

    nginx = read_text("deploy/nginx/tamanna-https.conf")
    for marker in (
        "server_name www.tamanna.com",
        "ssl_certificate",
        "ssl_certificate_key",
        "ssl_protocols TLSv1.2 TLSv1.3",
        "proxy_pass http://tamanna-ai:8000",
    ):
        if marker not in nginx:
            fail(f"Nginx configuration is missing: {marker}")

    deploy_script = read_text("deploy/deploy.sh")
    if "docker compose -f \"$COMPOSE_FILE\" up -d" not in deploy_script:
        fail("Deployment script does not start the Compose services")
    if "docker compose down -v" in deploy_script:
        fail("Deployment script must never delete persistent volumes")
    if "TAMANNA_SESSION_SECRET" not in deploy_script or "GEMINI_API_KEY" not in deploy_script:
        fail("Deployment script must validate private authentication and Gemini settings")

    dockerfile = read_text("Dockerfile")
    if 'CMD ["python", "-m", "uvicorn", "Main:app"' not in dockerfile:
        fail("Dockerfile does not start the expected FastAPI application")

    main_app = read_text("Main.py")
    if '@app.get("/health")' not in main_app:
        fail("Main.py is missing the unauthenticated container health endpoint")

    requirements = read_text("requirements-server.txt").lower()
    for dependency in ("httpx", "python-dotenv", "fastapi", "uvicorn"):
        if dependency not in requirements:
            fail(f"Server requirements are missing: {dependency}")

    package_json = ROOT / "package.json"
    if package_json.is_file():
        try:
            json.loads(package_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            fail(f"Invalid package.json: {exc}")

    print("PASS: Required website and self-hosted deployment files exist.")
    print("PASS: Private environment files are excluded from Docker context.")
    print("PASS: Compose health gating and localhost-only API binding are configured.")
    print("PASS: Account database and chat history use a persistent named volume.")
    print("PASS: Nginx TLS and Docker upstream configuration are present.")
    print("PASS: Deployment preflight completed.")
    print(
        "NOTE: This is a static check. DNS records, certificate validity, "
        "server firewall, host access, and live HTTPS must be tested on the "
        "actual hosting server."
    )


if __name__ == "__main__":
    main()
