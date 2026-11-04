<p align="center">
  <img src="assets/tamanna-logo.svg" alt="TI Tamanna AI Logo" width="280">
</p>

# Tamanna AI

Owner: HM INSAN ALI

## Verification status

**Development state: verification pending.** The repository now contains a FastAPI server entry point, a model-provider interface, SQLAlchemy persistence, authentication controls, and an allow-listed tool module. These components must not be treated as production-ready until the current GitHub Actions run completes successfully.

Latest server CI: [Tamanna AI Server CI](https://github.com/tamanna456760-it/Tamanna-/actions/workflows/Build.yml)

No successful end-to-end result is claimed in this README while that run is queued or failing.

## Repository entry points

- `Main.py` defines the FastAPI application.
- `run_server.py` is the launcher.
- `requirements-server.txt` lists the intended server runtime dependencies.
- `requirements-test.txt` adds the test dependencies.
- `.env.example` is a template only. It contains no real credentials.

## Local verification commands

Use Python 3.12 or newer in a clean virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-server.txt
python -m pip install -r requirements-test.txt
python -c "import Main"
python -m pytest -q
docker build -t tamanna-ai:local .
```

These are verification commands, not a statement that the current repository has passed them. Review the output before deployment.

## Private configuration

Copy `.env.example` to a local `.env`, then set both required credentials:

- `TAMANNA_SESSION_SECRET`: generate a unique value with `python -c "import secrets; print(secrets.token_urlsafe(48))"` (at least 32 characters).
- `GEMINI_API_KEY` (or `TAMANNA_MODEL_API_KEY`): your Gemini API key, required for AI chat.
- `TAMANNA_DATABASE_URL`: optional; the built-in SQLite database is used when this is blank or unset.
- `TAMANNA_CORS_ORIGINS`: exact trusted frontend origins, including `https://www.bd-king-r7.com`.

The server loads the repository-root `.env` before importing its application modules. Missing credentials are reported as readiness warnings without printing secret values: the website and health endpoint can start, while login or Gemini chat returns a clear configuration error until its setting is supplied.

Validate configuration locally (the report never prints credential values):

```sh
cp .env.example .env
# Edit .env and fill in the private credentials.
python scripts/validate_env.py
python scripts/validate_env.py --strict
``

The strict check fails until both authentication and Gemini credentials are configured. The normal check reports missing settings as warnings.

Never commit `.env`, API keys, session secrets, account databases, chat-history backups, or tool logs.

## Safety boundary

The chat endpoint is intended to call the configured model provider. The tool registry is limited to web search and read-only files under `data/docs/`. Command-execution endpoints are disabled by the access-control middleware. Do not re-enable them without a separate security review.

## Documentation

- [ROADMAP](ROADMAP.md): work that remains unverified or incomplete.
- [CI workflow review](docs/CI_WORKFLOWS_REVIEW.md): overlapping workflows retained for your review.

## Run Tamanna AI independently

This repository is the **Tamanna AI application**. It runs independently from the separate `Tamanna-server` repository. It does not start or depend on that Compose project.

Requirements: Docker Engine or Docker Desktop with Docker Compose.

1. Copy `.env.example` to `.env`.
2. Set a unique `TAMANNA_SESSION_SECRET` and your private `GEMINI_API_KEY` in `.env` if you want Gemini chat. Never commit `.env`.
3. From this repository folder, run:

```sh
docker compose up --build -d
docker compose ps
```

Tamanna AI application/API: http://127.0.0.1:8001
Health check: http://127.0.0.1:8001/health

To stop only Tamanna AI:

```sh
docker compose down
```

The container listens on port 8000 internally and is published on localhost port 8001 so it can run alongside the separate Tamanna Central Server, which uses localhost port 8000. Each repository has its own Compose project and data volume.

## Optional Tor v3 onion access

An optional Tor hidden-service container is included for the Tamanna AI application. It is separate from the Central Server repository and is started with this repository's Compose project.

Start both the AI app and Tor service:

```sh
docker compose up --build -d
docker compose ps
```

After the Tor container becomes healthy, read the **Tor-generated v3 hostname**:

```sh
docker compose exec -T tor cat /var/lib/tor/hidden_service/hostname
```

Tor creates and persists its private key in the `tamanna_tor_data` Docker volume. Back up that volume securely; losing the key changes the onion address. Do not publish or commit the private key.

**Important about the requested name:** `bd-king-r7.onion` cannot be assigned like a normal DNS domain. A v3 onion address is derived from its cryptographic key. The service therefore generates its own valid `.onion` hostname. Getting the exact vanity name `bd-king-r7.onion` would require a matching vanity key-generation search and cannot be guaranteed by configuration alone. The generated hostname is the working address until such a key exists.

The onion service forwards HTTP port 80 internally to the Tamanna AI app container. It does not expose a Tor SOCKS proxy or publish a public host port. Use Tor Browser to access the generated address.


## Central Server service protocol

Tamanna AI includes a small internal client at `tamanna_ai/integrations/central_server.py` for the signed `tamanna-service/1` report protocol. Configure `TAMANNA_SERVER_URL`, `TAMANNA_SERVER_KEY_ID`, and `TAMANNA_SERVER_SHARED_SECRET` in the private `.env` file. The shared secret must exactly match `TAMANNA_SERVICE_SHARED_SECRET` in the separate Tamanna-server repository. Generate it locally with `openssl rand -hex 32`; never commit it.

The client sends only the report payload you explicitly pass to `send_report(report)`. It does not run automatically, does not forward chat messages, and does not grant shell or remote code execution. Protocol specification: [Tamanna Central Server protocol v1](https://github.com/tamanna456760-it/Tamanna-server/blob/main/docs/TAMANNA_SERVICE_PROTOCOL_V1.md).


## Project-wide documentation and backend development

Tamanna AI includes prompt helpers for producing source-grounded project
documentation and database/backend implementation plans:

- `build_project_documentation_prompt()`: prepare a complete root README,
  verified API reference, and architecture overview from the repository tree
  plus relevant source/configuration excerpts.
- `build_database_backend_prompt()`: prepare SQL, MongoDB, REST, and GraphQL
  implementation requests with validation, authorization, owner isolation,
  safe migrations, error handling, and tests.

These helpers structure requests for the configured AI provider. They do not
automatically crawl the repository, write files, connect to a live database,
or deploy endpoints. Supply actual source files as context and verify generated
code and documentation before use.
