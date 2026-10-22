#!/usr/bin/env python3
"""
Tamanna AI — TLS Certificate Checker
Owner: HM INSAN ALI
Checks a public HTTPS endpoint's certificate.
Read-only network check; does not modify server configuration.
"""
import argparse
import json
import socket
import ssl
from datetime import datetime, timezone
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
def check_tls_certificate(hostname, port=443, timeout=8):
    result = {
        "project": PROJECT,
        "owner": OWNER,
        "hostname": hostname,
        "port": port,
        "status": "REVIEW_REQUIRED",
        "read_only": True,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "findings": [],
    }
    context = ssl.create_default_context()
    try:
        with socket.create_connection(
            (hostname, port), timeout=timeout
        ) as connection:
            with context.wrap_socket(
                connection, server_hostname=hostname
            ) as secure_socket:
                certificate = secure_socket.getpeercert()
                expires_text = certificate.get("notAfter")
                if not expires_text:
                    result["findings"].append(
                        "Certificate expiry date is unavailable."
                    )
                    return result
                expires = datetime.strptime(
                    expires_text, "%b %d %H:%M:%S %Y %Z"
                ).replace(tzinfo=timezone.utc)
                remaining_seconds = (
                    expires - datetime.now(timezone.utc)
                ).total_seconds()
                remaining_days = int(remaining_seconds // 86400)
                result["tls_version"] = secure_socket.version()
                result["certificate_expires_utc"] = (
                    expires.isoformat()
                )
                result["days_until_expiry"] = remaining_days
                if remaining_seconds <= 0:
                    result["findings"].append(
                        "TLS certificate has expired."
                    )
                elif remaining_days <= 30:
                    result["findings"].append(
                        "TLS certificate expires within 30 days."
                    )
                else:
                    result["status"] = "PASS"
    except (OSError, ssl.SSLError, ValueError) as exc:
        result["findings"].append(
            f"TLS check failed: {type(exc).__name__}: {exc}"
        )
    return result
def main():
    parser = argparse.ArgumentParser(
        description="Check a TLS certificate for a hostname."
    )
    parser.add_argument(
        "--host",
        default="www.tamanna.com",
        help="Hostname to check (default: www.tamanna.com)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=443,
        help="TLS port (default: 443)",
    )
    args = parser.parse_args()
    if not args.host or "/" in args.host:
        parser.error("--host must be a hostname, not a URL or path")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    report = check_tls_certificate(args.host, args.port)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
if __name__ == "__main__":
    main()