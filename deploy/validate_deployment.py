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
def validate_deployment(compose_path, nginx_path):
    findings = []
    compose_file = Path(compose_path)
    nginx_file = Path(nginx_path)
    compose_text = ""
    nginx_text = ""
    if not compose_file.is_file():
        findings.append(f"Compose file not found: {compose_file}")
    else:
        try:
            compose_text = compose_file.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(f"Cannot read Compose file: {exc}")
    if not nginx_file.is_file():
        findings.append(f"Nginx config not found: {nginx_file}")
    else:
        try:
            nginx_text = nginx_file.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(f"Cannot read Nginx config: {exc}")
    if compose_text:
        if "127.0.0.1:8000:8000" not in compose_text:
            findings.append(
                "App port 8000 is not explicitly bound to localhost."
            )
        if "no-new-privileges:true" not in compose_text:
            findings.append("no-new-privileges security option is missing.")
        if "443:443" not in compose_text:
            findings.append("HTTPS port 443 mapping is missing.")
        if "80:80" not in compose_text:
            findings.append("HTTP port 80 mapping is missing.")
        if "../.env" in compose_text:
            env_path = compose_file.parent / "../.env"
            if not env_path.resolve().is_file():
                findings.append("Referenced .env file does not exist.")
    if nginx_text:
        if "server_name www.tamanna.com" not in nginx_text:
            findings.append("Expected www.tamanna.com server_name is missing.")
        if "ssl_certificate" not in nginx_text:
            findings.append("TLS certificate directive is missing.")
        if "ssl_certificate_key" not in nginx_text:
            findings.append("TLS private-key directive is missing.")
        if "ssl_protocols TLSv1.2 TLSv1.3" not in nginx_text:
            findings.append("Expected TLS protocol policy is missing.")
        if "proxy_pass http://tamanna-ai:8000" not in nginx_text:
            findings.append(
                "Docker Nginx upstream should target tamanna-ai:8000."
            )
    return {
        "project": PROJECT,
        "owner": OWNER,
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "findings": findings,
        "read_only": True,
        "note": (
            "Text-based checks only. This does not parse Compose or Nginx "
            "syntax, validate certificates, or test network connectivity."
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
        "--nginx",
        default="deploy/nginx/tamanna-https.conf",
        help="Path to Nginx HTTPS configuration",
    )
    args = parser.parse_args()
    report = validate_deployment(args.compose, args.nginx)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
if __name__ == "__main__":
    main()