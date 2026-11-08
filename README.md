<p align="center">
  <img src="assets/tamanna-logo.svg" alt="TI Tamanna AI Logo" width="280">
</p>

# Tamanna AI

**Owner:** HM INSAN ALI

> AI chat application with a separate administrator workspace. The static interface can be opened without live APIs; live account data, privileged actions and AI responses require their respective backend services.

## Project dashboard

| Area | Open |
|---|---|
| User Chat | [Open Tamanna AI chat](https://www.bd-king-r7.com/) |
| Admin Control Center | [Open Admin Dashboard](https://www.bd-king-r7.com/admin/) |
| Source repository | [GitHub main branch](https://github.com/tamanna456760-it/Tamanna-/tree/main) |
| Build and CI status | [GitHub Actions](https://github.com/tamanna456760-it/Tamanna-/actions) |
| Server CI | [Tamanna AI Server CI](https://github.com/tamanna456760-it/Tamanna-/actions/workflows/Build.yml) |
| Remaining work | [ROADMAP.md](ROADMAP.md) |

**Admin allowlist:** `Tamanna456760@gmail.com`. The backend must verify this address against the private `TAMANNA_ADMIN_EMAIL` environment variable. A displayed email or hidden UI element is never authorization.

## What works without an API?

The static website can be built and previewed without Gemini, a database, or a running FastAPI server.

| Feature | No-API mode | Live service needed |
|---|---|---|
| Chat page layout and navigation | Yes | No |
| Admin dashboard layout and module navigation | Yes | No |
| Responsive design and static assets | Yes | No |
| Admin preview / API connection notice | Yes | No |
| Real sign-in and session verification | No | Authentication backend |
| AI-generated chat replies | No | Model provider + backend |
| Real user list, roles and account actions | No | Admin APIs + database |
| Live analytics, audit logs and security events | No | Backend + storage |
| Live server/deployment status | No | Monitoring integrations |
| Persistent settings and conversation memory | No | Backend + storage |

When the API is unavailable, the Admin page stays in **Preview Mode** and labels live information as pending. It must not invent statistics or enable privileged actions. Never put private credentials in browser JavaScript.

## Admin workspace modules

1. **Overview** — backend, model provider, environment and database connection state.
2. **User Management** — user directory, roles and account controls (backend integration pending).
3. **AI & API Settings** — provider/model configuration and usage limits (backend integration pending).
4. **Memory & Conversations** — storage health and retention controls (backend integration pending).
5. **Application Settings** — maintenance mode, feature flags, themes and language defaults (backend integration pending).
6. **Logs & Audit Trail** — login events, admin actions and application errors (backend integration pending).
7. **Security Center** — sessions, 2FA, rate limits and suspicious activity (backend integration pending).
8. **Server & Deployment** — build results, Cloudflare, backups and service health (integration pending).
9. **Analytics & Usage** — real activity, request volume, latency and quota reports (backend integration pending).

This is a control-center interface, not a claim that every backend operation is implemented. Each action must be connected to a permission-checked endpoint and tested before being marked live.

## Run the static app without APIs

Requirements: Node.js 20 or newer.

    npm ci
    npm run build
    npm run dev

To preview the generated production files:

    npm run build
    npm start

Open the local URL printed by the server. The static build includes both /admin.html and the clean /admin/ route. If the API is unavailable, the Admin page displays Preview Mode.

Cloudflare Workers static assets can serve the built frontend, but static deployment alone does not provide FastAPI endpoints, Gemini inference, authentication, database access, or privileged admin operations.

## Local AI model setup (no Gemini/GPT API)

Install Ollama on the same server as Tamanna AI, then pull a model that fits the server's RAM/VRAM. Example:

    ollama pull qwen2.5:7b
    ollama serve

Set `TAMANNA_MODEL_PROVIDER=ollama`, `TAMANNA_OLLAMA_URL=http://127.0.0.1:11434`, and `TAMANNA_OLLAMA_MODEL=qwen2.5:7b` in the private environment. Keep Ollama bound to localhost or a protected private network; do not expose port 11434 directly to the public internet. The selected model's quality and speed depend on its weights and available hardware. This connector does not claim Tamanna has trained its own foundation model.

## Run the FastAPI backend separately

Requirements: Python 3.12 or newer.

    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install -r requirements-server.txt
    python run_server.py

Use a private, untracked .env file for runtime configuration. See Private configuration below.

## Local verification

    npm ci
    npm run build
    npm test
    python -m compileall -q .
    python -m pytest -q

Run Python checks in an environment with server and test dependencies installed. These commands are instructions, not a claim that the latest commit has passed. Check [GitHub Actions](https://github.com/tamanna456760-it/Tamanna-/actions) for verified results before deployment.

## Private configuration

Copy .env.example to a local .env, then configure only the values needed for services you enable:

- `TAMANNA_ADMIN_EMAIL=Tamanna456760@gmail.com`: backend administrator allowlist.
- `TAMANNA_SESSION_SECRET`: generate a unique value with `python -c "import secrets; print(secrets.token_urlsafe(48))"` (at least 32 characters).
- `TAMANNA_MODEL_PROVIDER=ollama`: local model runtime (default; no hosted AI API key).
- `TAMANNA_OLLAMA_URL=http://127.0.0.1:11434`: private/local Ollama endpoint.
- `TAMANNA_OLLAMA_MODEL=qwen2.5:7b`: model name already pulled into the local runtime.
- The mock provider is test-only and requires `TAMANNA_ENV=test`.
- `TAMANNA_DATABASE_URL`: optional database URL; confirm backend-supported defaults before deployment.
- `TAMANNA_CORS_ORIGINS`: exact trusted frontend origins, including `https://www.bd-king-r7.com`.

Set secrets in the hosting provider's environment settings or in a local untracked .env. Never paste keys into README, HTML, JavaScript, commits, or public issues. The static-only frontend can run without these values; backend features cannot.

Validate configuration locally:

    cp .env.example .env
    # Edit .env locally; do not commit it.
    python scripts/validate_env.py
    python scripts/validate_env.py --strict

The strict check is expected to fail until required backend credentials are configured.

## Safety and access control

- Admin authorization must be enforced by the backend on every protected request.
- Admin Preview Mode grants no administrative privileges.
- Never expose session secrets, provider keys, database credentials or private user data to the frontend.
- Destructive actions require explicit confirmation, role checks, audit logging and tests.
- Keep command execution and arbitrary file-write routes disabled unless separately reviewed and securely restricted.
- Do not claim an operation succeeded unless the server confirms it.

## Repository entry points

- `index.html` — user-facing chat page.
- `admin.html` — Admin Control Center.
- `Main.py` — FastAPI application.
- `run_server.py` — backend launcher.
- `requirements-server.txt` — server runtime dependencies.
- `requirements-test.txt` — test dependencies.
- `scripts/build-static.js` — static site build, including /admin/.
- `wrangler.jsonc` — Cloudflare Workers static-assets configuration.
- `.env.example` — safe configuration template; no real credentials.

## Documentation

- [ROADMAP.md](ROADMAP.md) — incomplete and unverified work.
- [CI workflow review](docs/CI_WORKFLOWS_REVIEW.md) — workflow review notes.
- [GitHub Actions](https://github.com/tamanna456760-it/Tamanna-/actions) — build and test results.

## Deployment boundary

The current Cloudflare configuration describes a static-assets Worker. It can serve the chat and Admin interface, but it does not automatically proxy /api/* to FastAPI. Until backend hosting and secure routing are configured, treat the deployed Admin interface as a preview. Login, AI chat, user management and live monitoring are not guaranteed to work there.

Run locally as a static preview without APIs, or run FastAPI when private configuration is ready. Production deployment and live admin functionality require separate end-to-end verification.
