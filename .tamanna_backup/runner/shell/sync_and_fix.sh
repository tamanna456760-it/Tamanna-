#!/usr/bin/env bash
# /opt/bd-king-r7-powerhub/sync_and_fix.sh
# Purpose: pull repo, run fixers and build, update 'ficar' and 'power_sync' markers,
#          commit & optionally push changes, optionally run a power-sync hook.
set -euo pipefail

# === CONFIGURE THESE (edit before first run) ===
REPO_PATH="/home/youruser/projects/bd-king-r7"   # local git repo path
BRANCH="powerhub-auto"                           # dedicated branch for automated commits
REMOTE="origin"                                  # remote name
USER="youruser"                                  # system user that owns the repo and will run commands
FILE_FICAR="ficar"                               # file created/updated every run
FILE_POWERSYNC="power_sync"                      # marker file for power sync
PUSH_CHANGES=false                               # set to true to push commits to remote
# Define shell commands (arrays) to run fixers and builds.
# Use full commands (strings). They run in repo root, one after another.
FIX_CMDS=(
  "git submodule update --init --recursive || true"
  # JS/TS fixer example:
  # "npm ci --no-audit --no-fund || true"
  # "npx eslint --fix . || true"
  # Python example:
  # "python -m pip install -r requirements-dev.txt || true"
  # "black . || true"
)
BUILD_CMDS=(
  # Example placeholders. Replace with real project commands:
  # "npm ci && npm run build"
  # "make all"
  # "cargo build --release"
)
# Optional power sync hook (run after successful build). Leave empty to skip.
POWER_SYNC_CMD=""  # e.g. "./scripts/power_sync.sh" or "python tools/power_sync.py"
# Lock file to avoid overlapping runs
LOCKFILE="/var/lock/bd-king-r7-powerhub.lock"
LOGFILE="/var/log/bd-king-r7-powerhub.log"
# === END CONFIG ===

timestamp() { date --utc +"%Y-%m-%dT%H:%M:%SZ"; }

# Helper to log
log() {
  echo "[$(timestamp)] $*" | tee -a "${LOGFILE}"
}

# Ensure script runs as configured user when invoked by systemd (optional safety)
if [ "$(id -un)" != "${USER}" ]; then
  log "ERROR: Script running as $(id -un) but USER is set to ${USER}. Exiting."
  exit 1
fi

# Acquire lock to prevent overlapping runs
exec 9>"${LOCKFILE}"
if ! flock -n 9; then
  log "Another run is in progress. Exiting."
  exit 0
fi

if [ ! -d "${REPO_PATH}/.git" ]; then
  log "ERROR: ${REPO_PATH} is not a git repository. Exiting."
  exit 1
fi

cd "${REPO_PATH}"

log "Starting sync_and_fix for bd-king-r7 at branch ${BRANCH}"

# Fetch from remote (non-fatal)
git fetch --all --prune >>"${LOGFILE}" 2>&1 || log "git fetch failed (non-fatal)"

# Ensure we are on the automation branch; create if missing
if git rev-parse --verify "${BRANCH}" >/dev/null 2>&1; then
  git checkout "${BRANCH}" >>"${LOGFILE}" 2>&1 || { log "git checkout ${BRANCH} failed"; exit 1; }
else
  # create branch from remote/main (if present) or from HEAD
  if git ls-remote --exit-code "${REMOTE}" "main" >/dev/null 2>&1; then
    git checkout -b "${BRANCH}" "${REMOTE}/main" >>"${LOGFILE}" 2>&1 || git checkout -b "${BRANCH}" || true
  else
    git checkout -b "${BRANCH}" >>"${LOGFILE}" 2>&1 || true
  fi
fi

# Try to reset to remote branch to keep in sync if remote exists (avoid divergence)
if git ls-remote --exit-code "${REMOTE}" "${BRANCH}" >/dev/null 2>&1; then
  git reset --hard "${REMOTE}/${BRANCH}" >>"${LOGFILE}" 2>&1 || true
fi

# Pull latest changes (rebase preferred)
git pull --rebase "${REMOTE}" "${BRANCH}" >>"${LOGFILE}" 2>&1 || log "git pull (rebase) returned non-zero"

# Run fixers (lint --fix, codegen, formatters, etc.)
FIX_APPLIED=false
for cmd in "${FIX_CMDS[@]}"; do
  if [ -z "$cmd" ]; then continue; fi
  log "Running fixer: ${cmd}"
  set +e
  eval "${cmd}" >>"${LOGFILE}" 2>&1
  rc=$?
  set -e
  if [ $rc -ne 0 ]; then
    log "Fixer command failed (rc=${rc}): ${cmd} (continuing)"
  fi
done

# Stage all fixer-made changes (but we'll commit later only if something changed)
git add -A >>"${LOGFILE}" 2>&1 || true

# Run build/test commands sequentially
BUILD_OK=true
for cmd in "${BUILD_CMDS[@]}"; do
  if [ -z "$cmd" ]; then continue; fi
  log "Running build/test: ${cmd}"
  set +e
  eval "${cmd}" >>"${LOGFILE}" 2>&1
  rc=$?
  set -e
  if [ $rc -ne 0 ]; then
    log "Build/test failed (rc=${rc}) for: ${cmd}"
    BUILD_OK=false
    # optional: try to re-run fixers or codegen here; for now we stop further builds
    break
  fi
done

# Create/update 'ficar' and 'power_sync' marker files on every run
UUID="$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen || echo $RANDOM)"
echo "Updated at: $(timestamp)" > "${FILE_FICAR}"
echo "UUID: ${UUID}" >> "${FILE_FICAR}"
echo "Last successful build: $(timestamp) - BUILD_OK=${BUILD_OK}" > "${FILE_POWERSYNC}"

git add "${FILE_FICAR}" "${FILE_POWERSYNC}" >>"${LOGFILE}" 2>&1 || true

# Decide whether to commit & push
if git status --porcelain | grep -q .; then
  if [ "${BUILD_OK}" = true ]; then
    COMMIT_MSG="Automated sync/fix/build: $(timestamp)"
    git commit -m "${COMMIT_MSG}" >>"${LOGFILE}" 2>&1 || log "git commit failed"
    if [ "${PUSH_CHANGES}" = true ]; then
      if git rev-parse --verify "${REMOTE}/${BRANCH}" >/dev/null 2>&1; then
        git push "${REMOTE}" "${BRANCH}" >>"${LOGFILE}" 2>&1 || log "git push failed"
      else
        git push -u "${REMOTE}" "${BRANCH}" >>"${LOGFILE}" 2>&1 || log "git push failed"
      fi
    else
      log "PUSH_CHANGES is false; changes committed locally only"
    fi
  else
    log "Build failed; not committing fixer changes automatically. Changes are staged in working tree for inspection."
    # Leave changes unstaged for manual inspection: unstage to leave working tree
    git reset --mixed >>"${LOGFILE}" 2>&1 || true
  fi
else
  log "No changes detected; nothing to commit."
fi

# Optionally run the power sync command (only if provided and build_ok true)
if [ -n "${POWER_SYNC_CMD}" ] && [ "${BUILD_OK}" = true ]; then
  log "Running power sync hook: ${POWER_SYNC_CMD}"
  set +e
  eval "${POWER_SYNC_CMD}" >>"${LOGFILE}" 2>&1
  rc=$?
  set -e
  if [ $rc -ne 0 ]; then
    log "Power sync hook failed (rc=${rc})"
  else
    log "Power sync hook completed successfully"
  fi
fi

log "Finished sync_and_fix run"