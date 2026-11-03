# Tamanna AI — Central Server Integration and Build Report

Date: 2026-11-03
Branch: main
Scope: Tamanna AI application/client only. This report does not certify the separate Tamanna Central Server repository.

## Changes recorded in GitHub

- Added a dependency-free Python client for Central Server service protocol v1.
- Client signs the exact JSON request body using HMAC-SHA256.
- Client sends protocol version, key ID, Unix timestamp, unique nonce, and signature headers.
- Requires HTTPS for non-localhost server URLs.
- Requires a 64-character shared secret and returns controlled errors for HTTP/network failures.
- The client is opt-in: it does not automatically forward chat content or user data. An application caller must explicitly invoke send_report(report).
- Added unit tests for canonical request construction and HMAC-SHA256 output.
- Added private environment-variable configuration documentation.

## Verification status

- GitHub file updates: committed to main.
- Client unit tests: PENDING GitHub Actions result.
- Full application build and runtime: NOT YET CERTIFIED.
- Live connection to Central Server: NOT VERIFIED; private environment values and a running Central Server are required.

## Configuration required

Set these values in Tamanna AI's private, untracked .env:

- TAMANNA_SERVER_URL
- TAMANNA_SERVER_KEY_ID=tamanna-ai
- TAMANNA_SERVER_SHARED_SECRET

The shared secret must match the Central Server's TAMANNA_SERVICE_SHARED_SECRET. Generate it locally with openssl rand -hex 32; do not paste it into chat or commit it to GitHub.

## Integration boundary

Tamanna AI and Tamanna Central Server remain separate applications with independent startup. The client helper does not start the Central Server and does not send reports until explicitly called by application code.
