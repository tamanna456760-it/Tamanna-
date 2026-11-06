# Tamanna AI Backend Hosting Plan

Status: **HOSTING NOT DECIDED — NO PRODUCTION BACKEND DEPLOYMENT AUTHORIZED**

This document keeps the backend portable while the hosting provider is undecided.

## Current repository baseline

- Static frontend: Cloudflare Worker `titamanna`, built from `dist/`.
- Existing Python application: `Main.py`, imported by `run_server.py`.
- Container packaging: root `Dockerfile`.
- Local orchestration: root `docker-compose.yml`.
- Runtime dependencies: `requirements-server.txt`.
- Private environment template: `.env.example`.
- Frontend chat uses same-origin `POST /api/chat` in `js/chat.js`.

The existing Dockerfile runs the full FastAPI application with Uvicorn on port 8000, as a non-root user. Compose binds the service to localhost port 8001, drops Linux capabilities, enables no-new-privileges, limits PIDs, and persists the SQLite data directory in a volume.

## Hosting options (do not deploy until selected)

### Option A — Cloudflare Containers

Best candidate if the goal is to keep the existing Linux/Docker FastAPI application largely intact while keeping Cloudflare as the public edge.

- Reuse the root Dockerfile as the container image.
- Put a Cloudflare Worker in front of the container and route only `/api/*` to it.
- Keep the current static assets under `dist/`.
- Requires a Workers Paid plan and a container-compatible Worker configuration.
- Confirm persistent data strategy before production: container-local disk must not be treated as the only durable copy of user data. Move persistent data to a supported managed database/object store or a verified persistent volume strategy.

Cloudflare's static-frontend/container-backend example is the reference architecture:
https://developers.cloudflare.com/containers/examples/container-backend/

### Option B — Cloudflare Python Worker + D1

Best for a deliberately redesigned, lightweight serverless API.

- The prototype is in `cloudflare/backend/`.
- It is a separate implementation, not a deployment of root `Main.py`.
- D1 is a new database; SQLite accounts/history are not migrated automatically.
- Local filesystem project tools and code-execution features are not included.
- Validate Python Worker runtime compatibility, outbound Gemini calls, cookies, D1 bindings, migrations, and load/security tests before considering production.

Official references:
- https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
- https://developers.cloudflare.com/d1/examples/query-d1-from-python-workers/

### Option C — External Docker/Python host

Best if a conventional Linux Python runtime and persistent disk/PostgreSQL are preferred.

- Deploy the existing Dockerfile unchanged initially.
- Keep the backend private behind Cloudflare or a private service ingress.
- Add a Cloudflare route/proxy for `/api/*` to the selected backend origin.
- Configure persistent storage and database backups before onboarding users.

## API connection contract

The browser currently calls:

- `POST /api/chat` (same-origin)
- The API should expose the existing authentication and history routes already used by the frontend.

Target request flow:

```text
Browser
  -> https://www.bd-king-r7.com/api/*
  -> Cloudflare edge / API router
  -> selected FastAPI backend
  -> Gemini API and persistent database
```

Do not point the frontend directly at a temporary `workers.dev` URL. Prefer the same-origin `/api/*` path so cookies remain first-party and the frontend does not need a provider-specific URL.

Before enabling the route, verify that the selected backend supports:
- `POST /api/chat`
- Existing signup/login/logout/session endpoints
- Chat history and per-user data isolation
- HTTPS and secure cookie handling
- Correct trusted-origin/CSRF protections

## Security baseline

1. Store Gemini keys and session secrets only in the hosting provider's secret manager or a private `.env` file outside Git.
2. Generate a unique `TAMANNA_SESSION_SECRET` with at least 32 random bytes.
3. Use HTTPS end-to-end; enable secure, HttpOnly, SameSite cookies.
4. Keep CORS restricted to `https://www.bd-king-r7.com`; same-origin routing is preferred.
5. Enforce request-body limits, per-account and per-IP rate limits, login throttling, and bounded upstream timeouts.
6. Keep the backend origin private; do not expose the application port publicly if Cloudflare is the edge.
7. Run as non-root; drop capabilities; enable no-new-privileges; use read-only filesystem where compatible.
8. Persist user data outside ephemeral container filesystems; schedule encrypted backups and test restore.
9. Redact credentials, cookies, prompts, and personal data from logs.
10. Test authentication, authorization, rate limits, CORS, CSRF, IDOR, error handling, and backup restoration before production.

## Required secrets (only after a host is selected)

- `GEMINI_API_KEY` or `TAMANNA_MODEL_API_KEY`
- `TAMANNA_SESSION_SECRET`
- Optional search keys only if search is enabled: `TAVILY_API_KEY`, `BRAVE_SEARCH_API_KEY`
- Provider-specific deployment token only in CI secret storage, with least privilege.

Never put any of these values in source code, chat messages, screenshots, or committed files.

## Deployment gate

Do not deploy or change DNS until all are true:

- Hosting provider and plan confirmed.
- Database and persistent storage selected.
- Data migration and rollback plan documented.
- Secret manager populated privately.
- API route/proxy configured for `www.bd-king-r7.com/api/*`.
- Health check, signup/login/chat tests, and security tests pass.
- Backups and restore test pass.

**Current status:** Existing Docker packaging and environment template are present. The host, production database, API proxy, secrets, and live backend are not configured or verified.