<p align="center">
  <img src="assets/tamanna-logo.svg" alt="TI Tamanna AI Logo" width="280">
</p>

<h1 align="center">Tamanna AI</h1>

<p align="center">
  <strong>Your AI workspace. Built to grow under your control.</strong><br>
  Python · FastAPI · Gemini · Project Tools · Memory · Security
</p>

<p align="center">
  <a href="https://github.com/tamanna456760-it/Tamanna-">GitHub Repository</a> ·
  <a href="https://github.com/tamanna456760-it/Tamanna-/tree/main/docs">Documentation</a> ·
  <a href="https://github.com/tamanna456760-it/Tamanna-/issues">Issues & Support</a>
</p>

**Project owner:** HM INSAN ALI

Tamanna AI is a Python/FastAPI-based assistant project that brings together a web chat interface, Google Gemini integration, project utilities, memory components, agent modules and deployment/security tooling.

The repository includes active application code alongside experimental and legacy components. A module being present in the repository does not necessarily mean it is enabled in the production runtime.

## What the project includes

- **AI chat integration** — Gemini-backed chat endpoints in the main FastAPI application.
- **Agent modules** — Builder, coder, planner, reviewer, tester, monitor and deployer components.
- **Memory and knowledge** — Persistent JSON memory and documentation indexing utilities.
- **Project tooling** — Inspection and planning endpoints for supported project operations.
- **Security controls** — Admin API-key checks for privileged routes and a restricted read-only shell bridge.
- **Deployment foundation** — Docker Compose, Nginx reverse-proxy configuration and a static deployment preflight checker.
- **Automation checks** — GitHub Actions workflows for tests, static checks and repository audits.

## Architecture at a glance

The main application entry point is `Main:app`. The root `main.py` file is a compatibility launcher.

| Location | Responsibility |
|---|---|
| `Main.py` | Main FastAPI application, chat integration, middleware and API routes |
| `main.py` | Local application launcher |
| `tamanna_ai/integrations/gemini.py` | Gemini integration utilities |
| `tamanna_ai/agents/` | Agent components: builder, coder, planner, reviewer, tester, monitor and deployer |
| `tamanna_ai/core/controller.py` | Core controller interface |
| `tamanna_ai/memory/` | Memory components and persistent memory store |
| `tamanna_ai/knowledge/` | Documentation indexing and knowledge utilities |
| `app_security/auth.py` | Admin API-key verification |
| `data/linux/shell_bridge.py` | Restricted, read-only command bridge |
| `runner/python/` | Runner API; isolated build execution is not yet implemented |
| `deploy/` | Docker Compose, Nginx and deployment preflight |
| `tests/` | Automated test suite |
| `.github/workflows/` | CI and repository automation |

The package application at `tamanna_ai/api/server.py` is separate; it does not replace the main `Main:app` application.

## Quick start

### Requirements

- Python 3.11 or newer
- Git
- A Gemini API key if Gemini-powered chat is required

### 1. Get the source

```bash
git clone https://github.com/tamanna456760-it/Tamanna-.git
cd Tamanna-
```

### 2. Create an environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 3. Install server dependencies

```bash
python -m pip install -r requirements-server.txt
python -m pip install -r runner/python/requirements.txt
```

### 4. Configure private environment variables

```bash
cp .env.example .env
```

Edit `.env` locally or on your server. Set the required values:

```dotenv
GEMINI_API_KEY=your_private_gemini_api_key
GEMINI_MODEL=your_supported_gemini_model
TAMANNA_ADMIN_API_KEY=use_a_long_random_secret
TAMANNA_CORS_ORIGINS=http://127.0.0.1:8000
```

Use a real, supported model name for your Gemini account. Never paste real credentials into README files, source code, browser JavaScript, issues or chat logs. Never commit `.env`.

### 5. Start the application

```bash
python main.py
```

The launcher defaults to `127.0.0.1:8000`. Keep the service bound to localhost behind a properly configured reverse proxy in production.

## Configuration reference

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Private Gemini API credential |
| `GEMINI_MODEL` | Gemini model identifier |
| `TAMANNA_ADMIN_API_KEY` | Secret used to authorize privileged API operations |
| `TAMANNA_CORS_ORIGINS` | Comma-separated list of trusted frontend origins |
| `TAMANNA_MEMORY_FILE` | Optional path for the memory JSON file |
| `HOST` | Launcher bind host |
| `PORT` | Launcher port |

### Authentication notes

The admin API key is for machine-to-machine privileged API access. It is **not** a user login system, browser session, or substitute for account authentication.

- Protected endpoints fail closed if the admin key is not configured.
- Missing or invalid credentials are rejected.
- Do not expose the admin key in frontend code.
- Public chat and health endpoints are intentionally separate from privileged operations.

A complete user registration, login, session and account recovery system must be implemented and reviewed separately before describing Tamanna AI as having full user authentication.

## Security design

Current repository safeguards include:

- Admin-key verification on privileged operations.
- Restricted read-only shell commands rather than arbitrary shell execution.
- Process execution safeguards in the runner components.
- Nginx rate limiting configured for API traffic, with a 20 requests/second limit, burst allowance and connection cap.
- HTTPS and browser security-header configuration in the Nginx template.
- Read-only or manually gated automation in workflows where automatic source changes or pushes would be unsafe.

**Important:** Configuration files and static checks do not prove that a live server is secure. Review route permissions, secrets, workflow permissions, dependencies, network exposure and hosting configuration before production use.

## Docker deployment

Before deploying:

1. Configure a private root `.env` on the server.
2. Point the domain's DNS records to the intended hosting environment.
3. Install valid TLS certificate files at the paths expected by `deploy/nginx/tamanna-https.conf`.
4. Verify the Nginx configuration and Docker Compose file on the actual host.
5. Confirm that the application is reachable only through the intended reverse proxy.

Run:

```bash
docker compose -f deploy/docker-compose.yml config
docker compose -f deploy/docker-compose.yml up --build -d
docker compose -f deploy/docker-compose.yml ps
```

A successful Git commit, workflow run or static preflight does **not** prove that DNS, TLS, hosting access or the public website is working.

## Run checks

From the repository root:

```bash
python -m compileall -q Main.py main.py tamanna_ai app_security api core data runner scripts tests
python -m pytest -q
python scripts/audit_workflows.py
python deploy/preflight.py
```

Some environments may not have Docker installed; Docker image and live deployment checks must be run on a host that supports Docker.

Review GitHub Actions results before merging changes. A queued, cancelled or skipped workflow is not a passing test.

## Current implementation boundaries

The following items must not be treated as completed merely because related files or configuration exist:

- Full user login, registration, session management and account recovery.
- A production-grade isolated runner/build executor. The runner `/build` endpoint currently returns HTTP 501 until that executor exists.
- Live DNS, HTTPS certificate, reverse-proxy and hosting verification.
- Production deployment and operational monitoring.
- Complete security review of every route and every legacy workflow.

Any credential previously committed to Git history should be revoked and replaced. Removing a secret from the latest version of a file does not erase historical copies from Git history.

## Contributing safely

1. Work on a feature or repair branch; avoid editing `main` directly.
2. Inspect existing code before adding a new module or endpoint.
3. Keep secrets out of commits and logs.
4. Run the relevant tests and static checks.
5. Review workflow permissions and generated diffs before approving automation.
6. Merge only after required checks pass and the changes have been reviewed.

## Project documentation

- `docs/SECURITY_SETUP.md` — security configuration notes
- `docs/SYSTEM_MAP.md` — system architecture map
- `deploy/` — deployment configuration and preflight checks

## Contact

**Project owner:** HM INSAN ALI  
**Repository:** [tamanna456760-it/Tamanna-](https://github.com/tamanna456760-it/Tamanna-)
