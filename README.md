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

Copy `.env.example` to a local `.env` and set the values required by your environment. Generate a unique session secret locally. Put the Gemini API key in the private `.env` file only.

Never commit `.env`, API keys, session secrets, account databases, chat-history backups, or tool logs.

## Safety boundary

The chat endpoint is intended to call the configured model provider. The tool registry is limited to web search and read-only files under `data/docs/`. Command-execution endpoints are disabled by the access-control middleware. Do not re-enable them without a separate security review.

## Documentation

- [ROADMAP](ROADMAP.md): work that remains unverified or incomplete.
- [CI workflow review](docs/CI_WORKFLOWS_REVIEW.md): overlapping workflows retained for your review.
