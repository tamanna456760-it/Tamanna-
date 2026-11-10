# Safe Web Fetching Security Status

**Status: not approved for production browser access.** This document records the current boundary so the existing read-only fetcher is not mistaken for a hardened browser.

## What the current implementation does

`tamanna_ai/capabilities/web_fetch.py` currently:

- accepts absolute HTTPS URLs only and rejects embedded credentials;
- allows only the standard HTTPS port;
- rejects localhost and DNS answers that are not globally routable;
- validates each redirect target before following it;
- disables automatic redirects and environment proxy inheritance;
- limits redirects, request time, response bytes, and accepted content types;
- extracts HTML text without executing page JavaScript.

Regression tests cover mixed public/private DNS answers, private IPv6, non-standard ports, and private redirect targets.

## Remaining security blocker

The fetcher resolves and validates a hostname before requesting it, but the HTTP client performs its own hostname resolution when opening the connection. Those are separate operations. A hostname whose DNS answer changes between validation and connection could therefore create a DNS-rebinding / time-of-check-to-time-of-use (TOCTOU) SSRF risk.

The tests that validate a URL and its redirect target do **not** prove that the actual socket connects to the previously validated IP address.

## Required controls before enabling a Browser API

1. Implement a transport that pins the TCP destination to a validated public IP while preserving the original hostname for TLS SNI and certificate verification and the HTTP Host header. Do not rewrite an HTTPS URL to an IP address as a shortcut.
2. Revalidate every redirect and pin the destination for each new connection.
3. Add integration tests with a controlled DNS resolver and local test servers proving that a DNS answer changed after validation cannot redirect the socket to loopback, private, link-local, or reserved networks.
4. Enforce network-level egress restrictions as defense in depth, including IPv4 and IPv6 private, loopback, link-local, multicast, and metadata-service ranges. A proxy is acceptable only if it independently enforces equivalent destination checks.
5. Keep fetches authenticated, per-user rate-limited, bounded to a small number of URLs, and isolated from privileged internal services.
6. Test redirect loops, missing Location headers, timeout, oversized streamed bodies, unsupported content types, and malformed DNS responses.

## Integration status

- The FastAPI chat route currently does not expose a dedicated authenticated web-fetch endpoint.
- `CapabilityAssistant.chat(..., fetch_urls=...)` has an internal fetch capability, but that does not make it a public Browser API.
- The current website has no verified Browser Panel.
- GitHub Pages is static hosting and cannot run the FastAPI fetch backend.

Do not expose a user-supplied URL fetch endpoint or label this feature production-ready until the transport and egress controls above are implemented and tested.

## Safe next step

Prototype and review the connection-pinning transport against the exact locked HTTPX/httpcore versions before wiring any route or frontend. If the installed dependency versions cannot support a maintainable, testable transport, use a separately hardened egress proxy instead.
