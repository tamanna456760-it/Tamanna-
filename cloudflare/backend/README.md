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

## GitHub Actions deployment (optional)

For deployment from GitHub, add these repository Actions secrets:

- `CLOUDFLARE_API_TOKEN`: scoped token with Workers Scripts edit access for
  `tamanna-api`, D1 edit access for the account (to apply schema), and
  Workers Routes edit access for the `bd-king-r7.com` zone.
- `CLOUDFLARE_ACCOUNT_ID`: the Cloudflare account ID (not a secret, but keep
  it in the repository secret for consistent CI configuration).

Create the `tamanna-api` Worker once in Cloudflare Dashboard before using a
least-privilege per-Worker editor token. Creating a new Worker may require
Workers product Admin access. The route permission is needed because Wrangler
declares the `www.bd-king-r7.com/api/*` route in this config.

Also add runtime secrets to **Workers & Pages → tamanna-api → Settings →
Variables and Secrets**:

- `GEMINI_API_KEY`
- `TAMANNA_SESSION_SECRET` (at least 32 characters; generate a unique value)
- `GEMINI_MODEL` = `gemini-2.5-flash`

Then open **GitHub → Actions → Deploy Tamanna Python API to Cloudflare →
Run workflow**. The workflow applies the D1 schema and deploys the Worker.
The Gemini key and session secret must not be added to GitHub source files.

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
