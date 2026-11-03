# Tamanna Repository Architecture & Full-System Audit
Date: 2026-11-03
Repository: tamanna456760-it/Tamanna-
Audited ref: security/full-system-hardening
Default branch: main

## Scope and evidence
This is a structural audit based on the GitHub directory listings and README available on the audited branch. It is not a full execution audit: dependencies were not installed, source files were not all read line-by-line, test suites were not run, and no production host was accessed. Do not interpret this report as proof that the application builds or is production-ready.

## Confirmed top-level areas
- `core/`: boot identity, boot integrity, boot manager, boot manifest and boot banner/configuration.
- `tamanna_ai/`: application package, agents, authentication, integrations, memory, API, core controller, code builder, dispatcher, skills, and many feature packages.
- `app_security/`: security package including auth helper.
- `api/`: currently contains files named `system api` and `tamanna ai key`; these names need review and should not be treated as a canonical API package.
- `deploy/`: Docker Compose, deployment scripts, Nginx configuration, preflight checks, HTTPS smoke test, release validation and rollback documentation.
- `scripts/`: scanners, analyzers, repair tools, workflow audits, secret scanning, auth setup, health checks and repository repair utilities.
- `tests/`: access-control, API/server, core server, documentation indexer, Gemini integration and code-builder tests.
- `static/`: at least one system-panel JavaScript file.
- `.github/workflows/`: contains a mixture of workflow YAML and non-workflow source/assets.

## Application module map and intended responsibility
| Path | Responsibility | Required behavior / integration |
|---|---|---|
| `Main.py` and `main.py` | FastAPI application entrypoint and launcher | One canonical app factory, lifespan/startup checks, router registration, graceful shutdown, health/readiness endpoints |
| `tamanna_ai/core/controller.py` | Core orchestration/controller | Route requests to planner/agents/tools; enforce policy and timeouts; return structured results |
| `tamanna_ai/agents/planner.py` | Task planning | Produce validated, bounded plans; no direct privileged execution |
| `tamanna_ai/agents/builder.py`, `coder.py` | Build/code generation | Work in an isolated workspace; patch-based changes; never overwrite arbitrary paths |
| `tamanna_ai/agents/reviewer.py`, `tester.py` | Review and test | Review diffs, run allowlisted tests, report evidence; no automatic merge/deploy |
| `tamanna_ai/agents/monitor.py`, `deployer.py` | Monitoring/release | Health monitoring and gated deployment; require explicit approval and rollback |
| `tamanna_ai/integrations/gemini.py` | Gemini provider | Read API key only from server environment; request timeout, retry/backoff, model config, error redaction |
| `tamanna_ai/authentication/router.py` | Signup/login/session/profile routes | Password hashing, secure cookies, CSRF/origin controls, session revocation, rate limiting and account recovery design |
| `tamanna_ai/authentication/access_control.py` | Route authorization | Default-deny for privileged actions; role checks; tests for every sensitive route |
| `tamanna_ai/memory/` | Conversation/task/knowledge persistence | User-scoped storage, retention/deletion controls, encryption/backups and migrations |
| `tamanna_ai/api/server.py`, `routes.py` | API wiring | Versioned routes, request/response schemas, consistent error handling and auth dependencies |
| `app_security/` | Shared security primitives | Avoid duplicate auth implementations; one source of truth for security policy |
| `deploy/` | Self-host deployment | Reproducible image, non-root runtime, health/readiness checks, persistent data, TLS proxy and rollback |
| `scripts/` | Maintenance/audit commands | Read-only by default; explicit dry-run and allowlisted writes; never print secrets |
| `tests/` | Regression/integration tests | Unit + API + auth + provider-mocked + deployment configuration tests |

## Confirmed structural concerns
1. `.github/workflows/` is polluted with non-workflow files. The current listing includes Java, Python, JavaScript, shell, HTML, JSON, batch and miscellaneous files alongside workflow YAML. GitHub Actions only discovers supported workflow YAML files in this directory. Other files should be moved only after reference/import/runner checks.
2. Several workflow-looking files coexist with auto-run, auto-sync, auto-heal and auto-upgrade names. Their triggers, token permissions, checkout/ref behavior, shell execution and write operations need per-file review before enabling or deleting them.
3. The README is still generic in its project overview and includes placeholder technology/feature text. It does not describe the actual complete product architecture.
4. `tamanna_ai/api/api.py` is listed as zero bytes. Confirm whether it is intentionally unused; otherwise remove imports or implement it with tests.
5. Memory JSON files are zero bytes in the listing. Confirm whether these are intentionally empty seed files or abandoned storage; use the configured database/storage layer rather than treating JSON files as production persistence.
6. There are multiple security-related packages (`app_security`, `tamanna_ai/authentication`, `tamanna_ai/security`, `tamanna_ai/cyber_security`). Establish a clear boundary and avoid conflicting authorization implementations.
7. The root-level `api/` names contain spaces and are ambiguous. Determine whether they are documentation/artifacts or active modules before renaming.
8. Frontend structure is not yet established as a conventional app package from the inspected directories. The visible `static/` asset alone does not prove a complete mobile-responsive chat UI, settings, theme, voice, login and admin experience.
9. Deployment configuration exists, but static presence does not prove DNS, TLS, reverse proxy, container build, data persistence or live site health.
10. Previous branch notes describe a possible credential exposure in Git history. Revoke any exposed token at its provider and rotate it; deleting the current file does not invalidate a leaked credential.

## Recommended canonical layout (target, not a claim that all paths exist)
```
Main.py                         # FastAPI app factory / router composition
main.py                         # minimal launcher
tamanna_ai/
  api/                          # versioned API routers and schemas
  authentication/               # single auth + RBAC implementation
  core/                         # orchestration, policy, lifecycle
  agents/                       # planner, builder, coder, reviewer, tester, monitor
  integrations/                 # Gemini and provider adapters
  memory/                       # user-scoped persistence and migrations
  tools/                        # explicitly allowlisted tools
  knowledge/                    # document indexing and retrieval
  security/                     # shared policy and validation primitives
  web/                          # server-rendered/frontend integration if used
frontend/                        # only if a separate JS app is adopted
static/                          # built static assets
templates/                       # server-rendered templates if used
tests/                           # unit, integration, security and smoke tests
deploy/                          # compose, nginx, scripts, runbooks
scripts/                         # safe audit and maintenance CLI
docs/                            # architecture, API, operations and security
.github/workflows/               # supported workflow YAML only
```

## Feature-to-code checklist
- AI chat: chat router + provider adapter + conversation store + streaming/error handling + tests.
- Voice: browser microphone permission, speech-to-text/text-to-speech adapter, explicit consent, fallback text mode.
- Login/settings: auth router, user preferences, secure sessions, password reset/email verification provider, account deletion.
- Admin: RBAC policy, audit log, protected admin APIs, no admin privilege from email alone without controlled provisioning.
- Memory: per-user isolation, retention settings, export/delete, migrations, backup/restore.
- Tools/agents: tool registry, JSON schemas, allowlist, permission scopes, timeouts, sandbox; no unrestricted shell/file-write endpoints.
- File/project management: workspace root jail, path traversal defense, patch review, backups and rollback.
- Security: HTTPS, secure cookies, CSRF, CORS allowlist, rate limits, secret scanning, dependency scanning, audit logs.
- Deployment: pinned dependencies, image build, non-root container, health/readiness checks, persistent volumes, TLS renewal and tested rollback.
- UI: responsive chat-first layout, history/sidebar, attachments, voice controls, settings, themes, language selection and accessible states.

## Required verification gates before merge/deploy
1. Reconcile branch with current main and inspect conflicts; never force-push as a shortcut.
2. Validate every workflow trigger and set least-privilege permissions; disable auto-push/auto-deploy unless separately approved and protected.
3. Run Python compile/import checks and the full pytest suite in a reproducible environment.
4. Run frontend lint/build only if a real frontend package manifest exists.
5. Run secret scanning against current files and Git history; rotate any exposed credential.
6. Validate Compose and Docker build; inspect image contents for secrets.
7. Run local API smoke tests for health, auth, chat and protected endpoints.
8. Deploy only after explicit approval and access to the actual host; then verify HTTPS homepage, readiness and key APIs.

## Current outcome
This commit adds the architecture audit and implementation map only. No application source was rewritten, no mixed workflow-directory files were moved, no secrets were printed, no main-branch changes were made, and no live deployment was attempted. The next implementation phase must inspect each source module and its imports before making behavior-changing edits.
