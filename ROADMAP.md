# Tamanna AI Roadmap

This list contains work that is not yet verified as production-ready. Do not advertise these items as completed until the corresponding tests and deployment checks pass.

## Verification gates
- Complete the current GitHub Actions run for Python compilation, Bash syntax, JSON parsing, dependency closure, pytest, Docker build, and HTTP smoke tests.
- Resolve every failing test and rerun the full suite.
- Verify the local production environment and persistent data volume.
- Run the app with a local Ollama runtime and an installed model; confirm that an unavailable local runtime returns HTTP 503 without falling back to a hosted model.

## Data and account model
- Review the JSON-to-SQLite migration against a real legacy `data/chat_history.json` file. The migration creates a backup before import; verify the backup and row counts before deleting any legacy copy.
- The authentication router currently retains its separate SQLite account database. Plan and test a safe migration before consolidating authentication accounts with the SQLAlchemy `users` table.
- Add user-owned conversation IDs and history isolation before exposing a history endpoint.
- Define retention, export, deletion, and backup/restore behavior for conversations and memories.

## Model and tools
- Keep web search optional; if a provider is enabled, configure its secret privately and test its network/API failure paths.
- Add provider timeout, retry, and quota behavior with tests.
- Add an explicit policy for when the model may request the two allow-listed tools.
- Keep shell execution, eval, and user-supplied code execution disabled.

## Security and deployment
- Run protected-route tests against the complete deployed route table.
- Validate exact production CORS origins, HTTPS cookies, request-size limits, session rotation, and auth throttling.
- Test Docker persistence across container recreation.
- Verify DNS, TLS, reverse-proxy settings, and the live `/health` and `/api/chat` endpoints before production release.

## Frontend compatibility
- Confirm the existing frontend's chat payload and response handling against the API using browser-level tests.
- Add conversation selection only after user-scoped history is implemented and tested.
