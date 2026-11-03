#!/usr/bin/env python3
"""
Tamanna AI — Deployment Configuration Validator
Owner: HM INSAN ALI
Read-only checks for deployment configuration files.
Does not deploy, restart, or modify services.
"""
import argparse
import json
from pathlib import Path

PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
EXPECTED_HOST = "www.tamanna.com"


def validate_deployment(compose_path, nginx_path, require_env=False):
    findings = []
    compose_file = Path(compose_path)
    nginx_file = Path(nginx_path)
    compose_text = ""
    nginx_text = ""

    for file_path, label in (
        (compose_file, "Compose"),
        (nginx_file, "Nginx"),
    ):
        if not file_path.is_file():
            findings.append(f"{label} config not found: {file_path}")
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(f"Cannot read {label} config: {exc}")
            continue
        if label == "Compose":
            compose_text = content
        else:
            nginx_text = content

    if compose_text:
        required_compose = {
            "localhost-only app binding": "127.0.0.1:8000:8000",
            "no-new-privileges": "no-new-privileges:true",
            "persistent data volume": "tamanna_data:/app/data",
            "app healthcheck": "http://127.0.0.1:8000/health",
            "HTTP public listener": '"80:80"',
            "HTTPS public listener": '"443:443"',
        }
        for label, marker in required_compose.items():
            if marker not in compose_text:
                findings.append(f"Compose is missing {label}.")

        if "condition: service_healthy" not in compose_text:
            findings.append(
                "Nginx must wait until the app healthcheck succeeds."
            )
        if require_env and "../.env" in compose_text:
            env_path = compose_file.parent / "../.env"
            if not env_path.resolve().is_file():
                findings.append("Required server .env file does not exist.")

    if nginx_text:
        required_nginx = {
            "www domain": f"server_name {EXPECTED_HOST}",
            "apex domain redirect": "server_name tamanna.com",
            "TLS certificate": f"/etc/letsencrypt/live/{EXPECTED_HOST}/fullchain.pem",
            "TLS private key": f"/etc/letsencrypt/live/{EXPECTED_HOST}/privkey.pem",
            "TLS 1.2/1.3 policy": "ssl_protocols TLSv1.2 TLSv1.3",
            "Docker app upstream": "proxy_pass http://tamanna-ai:8000",
        }
        for label, marker in required_nginx.items():
            if marker not in nginx_text:
                findings.append(f"Nginx config is missing {label}.")

    return {
        "project": PROJECT,
        "owner": OWNER,
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "findings": findings,
        "read_only": True,
        "note": (
            "Text-based checks only. This does not parse Compose or Nginx "
            "syntax, verify domain ownership/DNS, validate certificates, "
            "or test network connectivity."
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate Tamanna AI deployment configuration."
    )
    parser.add_argument(
        "--compose",
        default="deploy/docker-compose.yml",
        help="Path to Docker Compose YAML",
    )
    parser.add_argument(
        "--require-env",
        action="store_true",
        help="Require the private server .env file to exist.",
    )
    parser.add_argument(
        "--nginx",
        default="deploy/nginx/tamanna-https.conf",
        help="Path to Nginx HTTPS configuration",
    )
    args = parser.parse_args()
    report = validate_deployment(args.compose, args.nginx, args.require_env)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
