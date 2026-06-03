#!/usr/bin/env bash
set -u

# Auto-install deps, format, lint, test and attempt fixes for Python and Node projects.
# Designed to be safe to run in CI and locally; errors are reported but don't abort early.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

EXIT_SUMMARY=0

log() { echo "[auto-build] $*"; }

# Python setup
PY_CMD="$(command -v python3 || command -v python || true)"
if [ -n "$PY_CMD" ]; then
  log "Detected Python: $PY_CMD"
  if [ -f requirements.txt ]; then
    log "Installing requirements.txt"
    "$PY_CMD" -m pip install -U pip wheel >/dev/null 2>&1 || true
    "$PY_CMD" -m pip install -r requirements.txt || EXIT_SUMMARY=1
  fi

  if [ -f requirements-dev.txt ]; then
    log "Installing requirements-dev.txt"
    "$PY_CMD" -m pip install -r requirements-dev.txt || EXIT_SUMMARY=1
  fi

  # Ensure formatters/linters are available (best-effort)
  "$PY_CMD" -m pip install -U black isort ruff autopep8 flake8 >/dev/null 2>&1 || true

  log "Running Python formatters"
  command -v black >/dev/null 2>&1 && black . || true
  command -v isort >/dev/null 2>&1 && isort . || true
  # ruff can apply fixes
  command -v ruff >/dev/null 2>&1 && ruff check . --fix || true
  # autopep8 as fallback
  command -v autopep8 >/dev/null 2>&1 && autopep8 --in-place --recursive . || true

  log "Running flake8 (non-fatal)"
  command -v flake8 >/dev/null 2>&1 && flake8 || EXIT_SUMMARY=1

  log "Running tests with pytest (if present)"
  if [ -f pytest.ini ] || [ -d tests ] || grep -q "pytest" <<<"$(git ls-files)" 2>/dev/null; then
    "$PY_CMD" -m pytest -q || EXIT_SUMMARY=1
  else
    log "No pytest tests detected — skipping pytest run"
  fi
else
  log "Python not found — skipping Python steps"
fi

# Node / JS setup
if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    log "Running npm ci"
    npm ci --no-audit --no-fund || true

    if command -v npx >/dev/null 2>&1; then
      log "Running eslint --fix (if available)"
      npx eslint . --fix || true
      log "Running prettier --write (if available)"
      npx prettier --write . || true
    fi
  else
    log "npm not found — skipping Node steps"
  fi
fi

log "Auto-build-and-fix completed (exit summary code: $EXIT_SUMMARY)"
exit $EXIT_SUMMARY
