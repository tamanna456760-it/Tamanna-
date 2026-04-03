#!/usr/bin/env bash
# Path: /opt/tamanna-sync/sync_and_add.sh
# Purpose: pull repo, add/update 'ficar' every run, commit & push if changes
set -euo pipefail

# === CONFIGURE THESE ===
REPO_PATH="/home/youruser/projects/tamanna"   # local git repo path
BRANCH="auto-ficar"                           # branch to operate on
REMOTE="origin"                               # remote name
FILE_NAME="ficar"                             # file to create/update
# If you want to push, make sure SSH keys/credentials are configured.
# === END CONFIG ===

LOGFILE="/var/log/tamanna-sync.log"

timestamp() { date --utc +"%Y-%m-%dT%H:%M:%SZ"; }

echo "=== $(timestamp) ===" >>"${LOGFILE}"
echo "Starting sync_and_add.sh" >>"${LOGFILE}"

if [ ! -d "${REPO_PATH}/.git" ]; then
  echo "ERROR: ${REPO_PATH} is not a git repository" | tee -a "${LOGFILE}"
  exit 1
fi

cd "${REPO_PATH}"

# Ensure clean and on branch
git fetch --all --prune >>"${LOGFILE}" 2>&1 || true
if git rev-parse --verify "${BRANCH}" >/dev/null 2>&1; then
  git checkout "${BRANCH}" >>"${LOGFILE}" 2>&1
else
  git checkout -b "${BRANCH}" >>"${LOGFILE}" 2>&1
fi

# Reset local branch to remote branch if remote exists (optional safe behavior)
if git ls-remote --exit-code "${REMOTE}" "${BRANCH}" >/dev/null 2>&1; then
  git reset --hard "${REMOTE}/${BRANCH}" >>"${LOGFILE}" 2>&1 || true
fi

# Update working tree
git pull --rebase "${REMOTE}" "${BRANCH}" >>"${LOGFILE}" 2>&1 || true

# Create or update the file 'ficar' with timestamp + UUID
UUID="$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen || echo $RANDOM)"
echo "Updated at: $(timestamp)" > "${FILE_NAME}"
echo "UUID: ${UUID}" >> "${FILE_NAME}"

# Stage and commit only if there are changes
if git status --porcelain --untracked-files=no | grep -q .; then
  git add "${FILE_NAME}" >>"${LOGFILE}" 2>&1
  COMMIT_MSG="Auto-update ${FILE_NAME} at $(timestamp)"
  git commit -m "${COMMIT_MSG}" >>"${LOGFILE}" 2>&1 || true

  # Push changes (requires auth setup). If push fails, log but don't crash.
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if git rev-parse --verify "${REMOTE}/${BRANCH}" >/dev/null 2>&1; then
      git push "${REMOTE}" "${BRANCH}" >>"${LOGFILE}" 2>&1 || echo "Push failed" >>"${LOGFILE}"
    else
      # push branch upstream
      git push -u "${REMOTE}" "${BRANCH}" >>"${LOGFILE}" 2>&1 || echo "Push failed" >>"${LOGFILE}"
    fi
  fi
else
  echo "No changes to commit." >>"${LOGFILE}"
fi

echo "Finished sync_and_add.sh" >>"${LOGFILE}"