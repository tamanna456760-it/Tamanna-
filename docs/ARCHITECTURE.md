# Tamanna AI — System Architecture

**Status:** Architecture baseline and migration guide  
**Owner:** HM INSAN ALI

## 1. Product boundaries

Tamanna AI is one product made of independently deployable components. Keep source ownership clear:

| Repository | Owns | Must not own |
|---|---|---|
| Tamanna- | Product app, shared AI modules, chat/admin frontend, Android source, tests, docs and CI | Production secrets or VPS runtime data |
| Tamanna-server | Central API/server runtime, database adapters, model runtime, security, operations and deployment | Public website source/assets |
| tamanna-website | Public website and links to app/admin | AI model runtime, private database or server secrets |

The server is the system of record for users, conversations, settings and audit events. Clients call it over HTTPS. GitHub stores source and build history; GitHub Pages is static hosting, not an AI inference server.

## 2. Logical architecture

~~~mermaid
flowchart TB
  subgraph Clients["Client applications"]
    WEB["Tamanna Chat UI"]
    ADMIN["Admin workspace"]
    ANDROID["Android client"]
    SITE["Public website"]
  end
  subgraph Edge["Delivery and edge"]
    CDN["Static hosting / CDN"]
    TLS["HTTPS reverse proxy / WAF"]
  end
  subgraph Server["Tamanna Central Server"]
    API["API gateway / FastAPI"]
    AUTH["Identity, sessions and RBAC"]
    ROUTER["Request and capability router"]
    CHAT["Chat orchestration"]
    TOOLS["Permission-scoped tools"]
    AUDIT["Audit, logs and metrics"]
  end
  subgraph Intelligence["Local intelligence"]
    MODEL["Local model runtime (Ollama adapter)"]
    RAG["Retrieval and knowledge index"]
    MEMORY["Conversation and user memory"]
    GH["Public Git repository knowledge sync"]
  end
  subgraph Data["Persistence"]
    DB[("Database")]
    FILES[("Private file storage")]
    BACKUPS[("Encrypted backups")]
  end
  WEB --> CDN
  ADMIN --> CDN
  SITE --> CDN
  ANDROID --> TLS
  CDN --> TLS --> API
  API --> AUTH
  API --> ROUTER --> CHAT
  CHAT --> MODEL
  CHAT --> RAG
  CHAT --> MEMORY
  CHAT --> TOOLS
  GH --> RAG
  AUTH --> DB
  MEMORY --> DB
  RAG --> DB
  API --> FILES
  API --> AUDIT
  DB --> BACKUPS
  FILES --> BACKUPS
~~~

## 3. Request lifecycle

1. A client sends a bounded HTTPS request.
2. The API validates request size, schema, origin and rate limits.
3. Authentication resolves the user and role; guest access is limited to explicitly public routes.
4. The router selects a capability and checks its permission policy.
5. Chat orchestration loads permitted conversation context and retrieves relevant knowledge.
6. The configured model adapter generates a response. Local Ollama is the default deployment target; hosted AI API keys are not required in that mode.
7. The server persists permitted conversation state and emits audit metadata without logging secrets.
8. The API returns a structured response with request ID and safe error information.

GitHub knowledge is a retrieval corpus, not a language model. Without a running local model, the system can search/index knowledge but cannot generate new AI answers.

## 4. Core module ownership

| Module | Responsibility | Boundary |
|---|---|---|
| API | HTTP routes, schemas and contracts | No model business logic in route handlers |
| Identity & Auth | Login, sessions, guest policy and roles | Backend authorization on every protected request |
| Core / Router | Capability selection and lifecycle | One routing policy; no duplicate dispatchers |
| AI Engine | Model adapters and generation | Local provider first; optional providers disabled unless configured |
| Knowledge | Import, chunking, indexing and retrieval | Provenance, deduplication and bounded indexing |
| Memory | Conversation/user memory | User isolation and retention policy |
| Tools / Agents | Explicitly registered capabilities | Allowlist, scoped permissions, timeouts and approval |
| Database | Repositories, migrations and transactions | No database access from browser code |
| Security | Validation, rate limits, headers and secrets | Fail closed for protected operations |
| Observability | Health, structured logs, metrics and audit | Never log passwords or tokens |
| Backup / Recovery | Backup, restore and integrity checks | Encrypted copies and tested restore |
| Frontend | Chat and admin presentation | UI is not an authorization boundary |
| Android | Mobile client | Uses documented API contracts |

## 5. Current implementation map

The current Tamanna- repository contains the legacy-compatible Main.py entrypoint, run_server.py, tamanna_ai package, root static frontend, tamanna-ai-app Android project, scripts, tests, cloudflare and deploy directories, plus historical/experimental paths. Preserve these until imports, workflow references and deployment dependencies have been audited.

See REPOSITORY_STRUCTURE.md for the current-to-target mapping. Website and central-server code must remain in their designated repositories.

## 6. Runtime profiles

### Static preview
Serves frontend assets only. It does not provide real AI generation, account sessions, privileged admin actions or persistent server data. The UI must label unavailable backend capabilities as preview/pending.

### Local development
FastAPI backend, SQLite development storage and a local model adapter. Local .env is untracked. A mock provider is test-only and must require an explicit test environment.

### Self-hosted production
Use an HTTPS reverse proxy, strict trusted origins, backend-only model endpoint and persistent database/storage. Ollama is private to the server network; never publish port 11434. Strong session secret, least-privilege service account, health checks, backups and monitoring are mandatory. No production claim until end-to-end health, chat, authentication, isolation and restore checks pass.

## 7. Security invariants

- Never commit .env, tokens, private runtime configuration, database files, user uploads or generated memory.
- Admin authorization is checked by the backend, not by hidden buttons or an email displayed in HTML.
- Guest chat, if enabled, has strict quotas and cannot access user/admin data.
- Database queries are scoped to the authenticated principal where applicable.
- Tool execution uses an allowlist, bounded arguments, timeouts and audit records.
- No arbitrary shell execution or unrestricted file-write endpoint is exposed to clients.
- Backups are encrypted and restore-tested.
- CI validates code and artifacts; it must not run destructive host operations or push unreviewed generated code.

## 8. CI/CD policy

- Only executable GitHub Actions workflows (.yml or .yaml) live directly under .github/workflows/.
- Helper scripts belong in .github/scripts/ or root scripts/, not beside workflow definitions.
- CI is read-only toward production unless a separate protected deployment workflow is approved.
- Use one canonical quality-gates workflow for shared Python, frontend and container checks. Keep specialist Android/security/deployment workflows only when coverage and triggers are documented.
- Do not use minute-by-minute workflow loops. Prefer event triggers and bounded schedules.
- A green workflow run is required evidence before claiming a build or test passed.

## 9. Migration sequence

1. Freeze a verified baseline and inventory paths, workflows, imports and generated files.
2. Keep the root entrypoint as a compatibility facade while moving one proven subsystem at a time into tamanna_ai/.
3. Add explicit package boundaries, typed interfaces and focused tests before moving each subsystem.
4. Consolidate duplicated workflows only after comparing triggers, permissions, secrets and job coverage.
5. Quarantine misplaced/obsolete files under trash/ only after reference scans and tests; do not delete backups or runtime configuration by guess.
6. Align Tamanna-server with central API ownership and connect clients only through documented HTTPS contracts.
7. Keep website source in tamanna-website; publish static app assets separately from backend deployment.
8. Run Python, Node, Android debug/release, Docker and deployment smoke tests independently. Record results and blockers.

## 10. Definition of done

Architecture work is complete only when the repository map matches the actual tree, documented entrypoints resolve, no workflow references missing files, CI tests pass, Android artifacts are produced, API chat works end-to-end with a local model, account isolation is verified, and production deployment plus backup restoration are independently tested.
