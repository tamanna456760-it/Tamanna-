#!/usr/bin/env bash
# Safe task dispatcher for the temporary GitHub-hosted Tamanna Linux runner.
set -Eeuo pipefail

TASK="${1:-}"
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

log() { printf '[tamanna-terminal] %s\n' "$*"; }
fail() { printf '::error::%s\n' "$*" >&2; exit 1; }

case "$TASK" in
  system-info)
    log "System information"
    uname -a
    python3 --version
    git --version
    df -h
    free -h
    ;;
  python-check)
    log "Compile Python files"
    python3 -m compileall -q .
    log "Python syntax compilation passed."
    ;;
  tests)
    [[ -d tests ]] || fail "No tests/ directory exists in this repository."
    python3 -m pip install --disable-pip-version-check pytest
    python3 -m pytest -q
    ;;
  repository-audit)
    log "Check tracked environment files"
    tracked_env="$(git ls-files | grep -E '(^|/)\.env$' || true)"
    [[ -z "$tracked_env" ]] || {
      printf '%s\n' "$tracked_env" >&2
      fail "Tracked .env file detected. Review it safely; do not print secrets."
    }
    log "No tracked .env file detected."
    git status --short
    ;;
  *)
    fail "Unsupported task. Choose: system-info, python-check, tests, repository-audit."
    ;;
esac
