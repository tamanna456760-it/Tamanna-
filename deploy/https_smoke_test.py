#!/usr/bin/env python3
"""
Tamanna AI — HTTPS Endpoint Smoke Test
Owner: HM INSAN ALI
Performs a read-only HTTPS GET request.
Does not change server or DNS configuration.
"""
import argparse
import json
import socket
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
def check_https(url, timeout=10):
    result = {
        "project": PROJECT,
        "owner": OWNER,
        "url": url,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "REVIEW_REQUIRED",
        "read_only": True,
        "findings": [],
    }
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        result["findings"].append(
            "A valid HTTPS URL is required."
        )
        return result
    if parsed.username or parsed.password:
        result["findings"].append(
            "URLs containing embedded credentials are not allowed."
        )
        return result
    context = ssl.create_default_context()
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TamannaAI-HTTPS-SmokeTest/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
            context=context,
        ) as response:
            result["http_status"] = response.status
            result["final_url"] = response.geturl()
            result["tls_verified"] = True
            result["status"] = (
                "PASS"
                if 200 <= response.status < 400
                else "REVIEW_REQUIRED"
            )
            if result["status"] != "PASS":
                result["findings"].append(
                    "Unexpected HTTP response status."
                )
    except urllib.error.HTTPError as exc:
        # HTTPError means the server returned an HTTP response.
        # Keep non-success responses as review-required.
        result["http_status"] = exc.code
        result["tls_verified"] = True
        result["findings"].append(
            f"Server returned HTTP status {exc.code}."
        )
    except (
        urllib.error.URLError,
        socket.timeout,
        TimeoutError,
        ssl.SSLError,
        OSError,
        ValueError,
    ) as exc:
        result["findings"].append(
            f"HTTPS request failed: {type(exc).__name__}: {exc}"
        )
    return result
def main():
    parser = argparse.ArgumentParser(
        description="Test a Tamanna AI HTTPS endpoint."
    )
    parser.add_argument(
        "--url",
        default="https://www.tamanna.com/",
        help="HTTPS endpoint to test",
    )
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 60:
        parser.error("--timeout must be between 1 and 60 seconds")
    report = check_https(args.url, args.timeout)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
if __name__ == "__main__":
    main()