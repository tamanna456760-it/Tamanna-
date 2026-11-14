# Repository Structure and File Placement

This is the target layout and migration contract. It does not claim that every directory already exists.

## 1. Repository ownership

- Tamanna-: app source, shared AI package, frontend preview, Android source, tests, docs and CI.
- Tamanna-server: central backend/server implementation and operational deployment.
- tamanna-website: public website only.

Never copy secrets, production data, local databases or generated model files between repositories.

## 2. Target layout for Tamanna-

~~~text
Tamanna-/
├── Main.py                    # legacy-compatible ASGI entrypoint
├── run_server.py              # supported backend launcher
├── index.html                 # user chat frontend
├── admin.html                 # admin frontend
├── css/                       # frontend styles
├── js/                        # frontend modules
├── assets/                    # committed static assets only
├── tamanna_ai/
│   ├── api/                   # routes and schemas
│   ├── core/                  # lifecycle, router and contracts
│   ├── ai_core/               # model adapters and inference
│   ├── agents/                # permission-scoped orchestration
│   ├── authentication/        # identity and sessions
│   ├── knowledge/              # ingestion, index and retrieval
│   ├── memory/                 # conversation/user memory
│   ├── database/               # repositories and migrations
│   ├── security/               # policy and validation
│   ├── tools/                  # allowlisted tools
│   ├── integrations/           # optional adapters
│   └── observability/          # logs, metrics and audit
├── tamanna-ai-app/             # Android project
├── cloudflare/                 # edge/static adapter only
├── config/                     # safe defaults; no secrets
├── deploy/                     # container and proxy templates
├── scripts/                    # maintained developer/CI utilities
├── tests/                      # Python and integration tests
├── docs/                       # architecture and operations
├── data/                       # runtime data; Git-ignored
├── logs/                        # runtime logs; Git-ignored
├── trash/                       # reviewed quarantine copies
├── .github/
│   ├── scripts/                 # workflow helper scripts
│   └── workflows/               # only *.yml / *.yaml Actions files
├── .env.example
├── requirements-server.txt
├── requirements-test.txt
├── package.json
├── Dockerfile
├── docker-compose.yml
└── README.md
~~~

## 3. Current-to-target mapping

| Current component | Target ownership | Rule |
|---|---|---|
| Main.py, run_server.py | Root entrypoints | Keep compatibility; no competing server entrypoints |
| tamanna_ai/ | Python application package | Use existing domain packages; avoid parallel duplicates |
| index.html, admin.html, css/, js/, assets/ | Static frontend | No secrets or server-only logic in browser code |
| tamanna-ai-app/ | Android | Keep Gradle wrapper, manifest, resources and source together |
| cloudflare/ | Edge adapter | Static assets/edge functions; not a replacement for model server |
| scripts/ | Maintained utilities | Every script has a documented purpose and safe defaults |
| tests/ | Application tests | Mirror package domains and test public contracts |
| .github/workflows/ | CI/CD definitions | Workflow YAML only; helper code lives elsewhere |
| data/, logs/ | Runtime state | Never commit user data, databases or generated logs |
| trash/ | Quarantine | Preserve original path and reason; never run as active code |

## 4. Python package rules

- Use lowercase snake_case module and package names.
- Add __init__.py to importable packages where required by supported Python/tooling.
- Route handlers validate and delegate; they do not implement inference or persistence.
- Keep provider-specific code behind a common adapter interface.
- Avoid circular imports; dependencies flow toward core contracts, not from core into optional integrations.
- Do not create a second implementation of memory, routing, auth or database access without a documented replacement plan.

## 5. Frontend rules

- Use lowercase descriptive filenames such as chat.js, auth.js and settings.js.
- Keep presentation, API client and state management separate.
- The frontend calls documented API paths; it never connects directly to SQLite, Ollama or private storage.
- Admin UI is not an authorization layer. The backend verifies every privileged operation.
- Keep the static preview honest when the backend is offline.

## 6. Workflow rules

- Only valid GitHub Actions workflow files (.yml / .yaml) live in .github/workflows/.
- Java, Python, shell, batch, HTML, JSON and Dart helper/source files belong in their owning source folders.
- Before relocating a file, search imports, run/uses paths, package scripts, Docker contexts and documentation.
- Prefer one canonical validation workflow plus separately justified Android, security and deployment workflows.
- Use least-privilege permissions, pinned actions where practical, concurrency controls and explicit deployment approvals.
- Never add self-modifying loops, force pushes or unbounded one-minute jobs.

## 7. Naming and documentation

- Python: snake_case.py; classes: PascalCase.
- JavaScript: camelCase.js; CSS: kebab-case.css.
- Tests: test_<feature>.py or <feature>.test.js.
- Docs: descriptive Markdown names; preserve established operational doc names.
- Every maintained script/workflow states purpose, trigger, inputs, outputs and failure behavior.

## 8. Safe cleanup checklist

1. Record current path and blob SHA.
2. Search all code and configuration references.
3. Inspect the file; do not infer its purpose from its name.
4. Check workflow triggers, secrets, permissions and side effects.
5. Move to trash/quarantine-<date>/ with a manifest preserving original path and reason.
6. Run relevant tests and verify the new path.
7. Delete only after explicit approval and a verified backup.

No broad folder moves or deletions are authorized by this document.
