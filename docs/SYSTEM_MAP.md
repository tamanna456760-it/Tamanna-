# Tamanna AI — System Map and Setup

Owner: HM INSAN ALI

## Main runtime

| Path | Responsibility |
|---|---|
| `Main.py` | Main FastAPI app, browser chat route, CORS and existing API routes |
| `main.py` | Local compatibility launcher |
| `Dockerfile` | Production image; starts `Main:app` on `0.0.0.0:8000` |
| `deploy/docker-compose.yml` | Production app + Nginx containers and private Docker network |
| `deploy/nginx/tamanna-https.conf` | HTTPS reverse proxy for tamanna.com and www.tamanna.com |

## AI and application modules

| Path | Responsibility / current limit |
|---|---|
| `tamanna_ai/integrations/gemini.py` | Async Gemini client; needs GEMINI_API_KEY |
| `tamanna_ai/agents/` | Builder, coder, planner, reviewer, tester, monitor and deployment preflight |
| `tamanna_ai/core/controller.py` | Lightweight core controller; not a replacement for Main.py chat endpoint |
| `tamanna_ai/brain/brain.py` | In-process basic knowledge/memory helper |
| `tamanna_ai/memory/memory_store.py` | Persistent JSON memory store with atomic writes |
| `tamanna_ai/knowledge/documentation_indexer.py` | Documentation indexing component |
| `tamanna_ai/api/server.py` | Separate package API; not the production entry point |
| `tamanna_ai/tools/echo_power.py` | Basic echo and process status helper |

## Security and execution boundaries

- `app_security/auth.py` validates the X-API-KEY header against TAMANNA_ADMIN_API_KEY.
- Protected admin and internal project-inspection routes fail closed with HTTP 503 when the admin key is absent.
- Public chat and health remain available; the admin key is not a browser login token.
- Nginx limits API traffic to 20 requests/second per client (1,200/minute), burst 40 and 20 concurrent connections; excess requests receive HTTP 429.
- HTTPS responses include HSTS, frame, content-type, referrer and permissions policy headers.
- `data/linux/shell_bridge.py` is intentionally read-only and allow-listed.
- `runner/python/server.py` authenticates its build endpoint but returns HTTP 501 until a real isolated executor is implemented.
- Never store API keys, tokens, certificates or private keys in Git. Configure them in a private root `.env` or a hosting secrets manager.
- A key that appeared in Git history must be revoked/rotated; deleting the latest copy does not remove historical copies.

## Setup and validation

1. Create the root `.env` from `.env.example` on the server only.
2. Configure GEMINI_API_KEY if Gemini chat is required.
3. Generate a strong TAMANNA_ADMIN_API_KEY before enabling privileged routes.
4. Install server dependencies with `python -m pip install -r requirements-server.txt`.
5. Install runner dependencies with `python -m pip install -r runner/python/requirements.txt`.
6. Run locally with `python main.py`.
7. Validate the production Compose config with `docker compose -f deploy/docker-compose.yml config`.
8. Start production only after DNS and Let's Encrypt certificate files exist: `docker compose -f deploy/docker-compose.yml up --build -d`.
9. Run tests with `python -m pytest -q`.

## CI policy

- Python Tests and Full Code Test System compile Python sources and run pytest.
- Broad automatic execution of every Python file is disabled.
- Automatic source rewriting and automatic pushes are disabled.
- Changes must be reviewed on the repair branch and merged only after successful CI.

## Not yet certified

GitHub commits do not prove that the production server, DNS, TLS certificates, firewall, Nginx, domain ownership or live website are working. These require checks on the actual hosting provider. CI runs currently remain queued, so tests are not yet confirmed passing.