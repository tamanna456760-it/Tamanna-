# Tamanna AI — Cloudflare Python API

A separate API Worker; it does not replace the existing static Worker `titamanna`
or its `dist/` deployment.

## Architecture

- Python Worker + FastAPI ASGI adapter.
- D1 stores accounts, hashed sessions, preferences, and chat history.
- Gemini API key is stored as a Worker secret.
- Route: `https://www.bd-king-r7.com/api/*`.
- Existing frontend paths `/api/chat` and `/api/auth/*` remain same-origin.

The root `Main.py` is not imported: it uses local filesystem and SQLite /
SQLAlchemy storage. Those project tools require separate D1/R2 adapters.
This Worker provides the first Cloudflare-native account and chat API.

## Setup

From this directory:

```sh
npx wrangler d1 create tamanna-ai-db
```

Replace `REPLACE_WITH_CLOUDFLARE_D1_DATABASE_ID` in `wrangler.jsonc`
with the returned ID, then apply the production schema:

```sh
npx wrangler d1 execute tamanna-ai-db --remote --file=./schema.sql
uv sync
uv run pywrangler dev
```

Copy `.dev.vars.example` to `.dev.vars` for local development.

## Production secrets

```sh
npx wrangler secret put GEMINI_API_KEY
npx wrangler secret put TAMANNA_SESSION_SECRET
npx wrangler secret put GEMINI_MODEL
```

Generate the session secret locally:

```sh
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Never paste credentials into chat or commit them to GitHub.

## Deploy and verify

```sh
uv run pywrangler deploy
curl -i https://www.bd-king-r7.com/api/status
```

Expected response reports `status: online` and `database: connected`.
The route requires the `bd-king-r7.com` zone to be active in this Cloudflare
account. If route registration fails, attach the same route in the dashboard.

## Important limitations before production

1. This creates a new D1 account store. Existing SQLite accounts and chat
   history are not migrated automatically; export and migrate them before
   switching existing users.
2. Local filesystem project tools, skill/code-builder operations, and other
   `Main.py` routes are not included yet. They need Cloudflare-compatible
   storage/execution design using D1, R2, Queues, or Containers.
3. Python Workers are in open beta. Run signup/login/chat tests and inspect
   Worker logs before calling the service production-ready.
