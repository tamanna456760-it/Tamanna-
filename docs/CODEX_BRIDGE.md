# Tamanna AI — Codex bridge

## What this adds

The optional `/api/codex` router lets an authenticated Tamanna administrator submit a bounded task to the Codex CLI installed in the same backend runtime. It is **not** a Codex Cloud API and it does not make a browser-only Codespace editor remotely executable by itself.

- `GET /api/codex/status`: admin-only readiness information.
- `POST /api/codex/tasks`: admin-only task execution.
- The working directory is fixed to the Tamanna repository (or a configured subdirectory inside it); request data cannot choose a path or command.
- Execution uses argument arrays with `shell=False`, a bounded timeout, and a capped output.
- Read-only sandbox is the default.
- Write access requires both request confirmation (`write_access=true`, `confirm_write=true`) and the private server setting `TAMANNA_CODEX_WRITE_ENABLED=true`.
- The bridge is disabled unless `TAMANNA_CODEX_ENABLED=true`.

## Runtime requirements

The host/container that runs `Main.py` must have the Codex CLI installed and authenticated as the intended operator. Authentication in a user's separate Codespaces browser session is not automatically inherited by the production backend or Docker container.

Configure these only in the private runtime environment, never commit credentials:

```dotenv
TAMANNA_CODEX_ENABLED=false
TAMANNA_CODEX_WRITE_ENABLED=false
TAMANNA_CODEX_WORKSPACE=/app
TAMANNA_CODEX_TIMEOUT=600
```

After installing and authenticating Codex in a dedicated, isolated runtime, enable read-only mode first. Verify `GET /api/codex/status` reports enabled and installed. Only then consider enabling workspace-write mode. Do not use Codex's dangerous full-access / yolo mode. Keep the runtime isolated, backed up, and restricted to the repository.

## Important limitations

- This bridge executes Codex locally where the FastAPI backend runs; it does not call a Codex Cloud task endpoint.
- If Codex is installed only in a separate Codespaces session, the deployed backend cannot access it. Install/authenticate Codex in the backend runtime or build a separately authenticated remote worker.
- A Codespace is a development environment, not a durable production VPS. It may stop when its usage quota or lifecycle policy requires.
- Review diffs and run tests before merging or deploying any Codex-generated changes.
