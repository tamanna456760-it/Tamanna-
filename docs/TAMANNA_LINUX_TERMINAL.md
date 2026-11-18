# Tamanna Linux Terminal

This terminal runs as a **manual GitHub Actions job** on a temporary Ubuntu runner. It is not a persistent VPS or an interactive SSH shell.

## Run it

1. Open the repository's **Actions** tab.
2. Select **Tamanna Linux Terminal**.
3. Choose **Run workflow** on the `main` branch.
4. Select one task and start the workflow.
5. Read the job logs and the run summary.

## Tasks

| Task | What it does |
|---|---|
| `system-info` | Prints Linux, Python, Git, disk and memory information |
| `python-check` | Compiles Python files to check syntax |
| `tests` | Installs pytest and runs the root `tests/` suite; fails clearly if absent |
| `repository-audit` | Checks for a tracked exact `.env` file and prints working-tree status |

## Files

- Workflow: `.github/workflows/tamanna-linux-terminal.yml`
- Task runner: `scripts/tamanna-linux-terminal.sh`

## Security and limits

- Workflow permission is read-only: `contents: read`.
- Checkout does not persist the GitHub token.
- No arbitrary command input, privileged mode, secret output, or automatic deployment is provided.
- The GitHub-hosted runner is destroyed after each run. Use a separately secured self-hosted runner for persistent workloads; do not expose an unauthenticated shell to the internet.
