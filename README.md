<p align="center">
  <img src="assets/tamanna-logo.svg" alt="TI Tamanna AI Logo" width="280">
</p>

# Tamanna AI

**Owner:** HM INSAN ALI

Tamanna AI is a Python/FastAPI application with a web chat interface, Gemini integration, project tools, memory components, agent modules and deployment/security utilities. The repository also contains legacy and experimental modules; not every module is active in the production runtime.

## Main architecture

| Path | Purpose |
|---|---|
| `Main.py` | Main FastAPI application, chat routes, middleware and API endpoints |
| `main.py` | Compatibility launcher |
| `tamanna_ai/integrations/gemini.py` | Gemini client; requires a private API key |
| `tamanna_ai/agents/` | Builder, coder, planner, reviewer, tester, monitor and deployer |
| `tamanna_ai/core/controller.py` | Lightweight controller interface |
| `tamanna_ai/memory/memory_store.py` | Persistent JSON memory store |
| `tamanna_ai/knowledge/documentation_indexer.py` | Documentation indexing |
| `app_security/auth.py` | Admin API-key verification |
| `data/linux/shell_bridge.py` | Restricted read-only command bridge |
| `runner/python/server.py` | Authenticated runner API; build returns HTTP 501 until an isolated executor exists |
| `deploy/` | Docker Compose, Nginx and deployment preflight |

The production ASGI entry point is `Main:app`. The package API in `tamanna_ai/api/server.py` is separate and is not a replacement for the main application.

## Local setup

Use Python 3.11+:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-server.txt
python -m pip install -r runner/python/requirements.txt
cp .env.example .env
```

Edit the private `.env` file on the server or local machine. Configure a fresh `GEMINI_API_KEY` if Gemini chat is required and a strong `TAMANNA_ADMIN_API_KEY` for privileged operations. Never commit `.env`, API keys, tokens, certificates or private keys.

Run locally:

```bash
python main.py
```

The launcher defaults to `127.0.0.1:8000`.

## Environment variables

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Private Gemini credential |
| `GEMINI_MODEL` | Gemini model selection |
| `TAMANNA_ADMIN_API_KEY` | Machine-to-machine key for privileged API routes |
| `TAMANNA_CORS_ORIGINS` | Comma-separated trusted frontend origins |
| `TAMANNA_MEMORY_FILE` | Optional memory JSON path |
| `HOST`, `PORT` | Local launcher bind address and port |

If the admin key is missing, protected endpoints return HTTP 503. Missing or incorrect request keys return HTTP 401 or 403. The admin key is not a user login/session token and must never be placed in browser JavaScript. Public chat and health endpoints remain public.

## API and reverse-proxy security

Nginx applies per-client API rate limiting at 20 requests/second (1,200/minute), burst 40, and a 20-connection cap. Excess requests receive HTTP 429. It also configures HTTPS and browser security headers. Verify Nginx syntax on the actual server before deployment.

The shell bridge is read-only and allow-listed. Arbitrary shell execution is intentionally disabled. The runner `/build` endpoint returns HTTP 501 until a real isolated executor is implemented.

## Docker deployment

Before starting production, configure the private root `.env`, point DNS to the server, and install valid Let's Encrypt certificate files at the paths used by `deploy/nginx/tamanna-https.conf`.

```bash
docker compose -f deploy/docker-compose.yml config
docker compose -f deploy/docker-compose.yml up --build -d
docker compose -f deploy/docker-compose.yml ps
```

A successful GitHub commit does not prove DNS, TLS, hosting access or the live website is working.

## Tests

```bash
python -m compileall -q Main.py main.py tamanna_ai app_security api core data runner scripts tests
python -m pytest -q
python scripts/audit_workflows.py
python deploy/preflight.py
```

GitHub Actions run syntax checks, tests, deployment preflight and Docker build checks. Broad automatic execution, unreviewed source rewriting and automatic pushes are disabled.

## Security status and limitations

- Rotate any credential that has ever appeared in Git history. Deleting the latest file does not remove historical copies.
- Review all routes, dependencies, chat-driven actions and workflow permissions before production.
- The runner build executor, full user login/session system, live DNS/TLS checks and production deployment still require implementation or verification.
- CI results must be green before merging the repair branch into `main`.

## Contact

Project maintainer: Tamanna AI repository owner.
