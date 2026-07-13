#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/opt/bd-king-r7"
STAGING_DIR="$REPO_DIR/staging"
ARCHIVE_DIR="$REPO_DIR/archives"
LOG_DIR="$REPO_DIR/logs"
BRANCH="main"

mkdir -p "$STAGING_DIR" "$ARCHIVE_DIR" "$LOG_DIR"

while true; do
  TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
  echo "[$TIMESTAMP] 🔄 Starting auto-build cycle" >> "$LOG_DIR/auto_build.log"

  # Sync
  git -C "$REPO_DIR" fetch --all --prune >> "$LOG_DIR/auto_build.log" 2>&1 || true
  git -C "$REPO_DIR" checkout "$BRANCH" >> "$LOG_DIR/auto_build.log" 2>&1
  git -C "$REPO_DIR" pull origin "$BRANCH" >> "$LOG_DIR/auto_build.log" 2>&1

  # Stage new code
  rsync -a --delete "$REPO_DIR/src/" "$STAGING_DIR/" >> "$LOG_DIR/auto_build.log" 2>&1

  # Preflight checks
  echo "[$TIMESTAMP] 🔒 Running license and security checks" >> "$LOG_DIR/auto_build.log"
  ./scripts/license_check.sh "$STAGING_DIR" >> "$LOG_DIR/auto_build.log" 2>&1 || { echo "License check failed"; sleep 60; continue; }
  ./scripts/security_scan.sh "$STAGING_DIR" >> "$LOG_DIR/auto_build.log" 2>&1 || { echo "Security scan failed"; sleep 60; continue; }

  # Build
  echo "[$TIMESTAMP] ⚙️ Building" >> "$LOG_DIR/auto_build.log"
  ./scripts/build.sh "$STAGING_DIR" >> "$LOG_DIR/auto_build.log" 2>&1
  BUILD_EXIT=$?

  if [ $BUILD_EXIT -eq 0 ]; then
    echo "[$TIMESTAMP] ✅ Build succeeded" >> "$LOG_DIR/auto_build.log"
    # Archive artifact
    tar -czf "$ARCHIVE_DIR/build-$TIMESTAMP.tar.gz" -C "$STAGING_DIR" . >> "$LOG_DIR/auto_build.log" 2>&1
    # Integrate
    rsync -a --delete "$STAGING_DIR/" "$REPO_DIR/src/" >> "$LOG_DIR/auto_build.log" 2>&1
    ./scripts/update_registry.sh >> "$LOG_DIR/auto_build.log" 2>&1
  else
    echo "[$TIMESTAMP] ❌ Build failed" >> "$LOG_DIR/auto_build.log"
    ./scripts/fallback_notify.sh "$TIMESTAMP" >> "$LOG_DIR/auto_build.log" 2>&1
  fi

  # Throttle and wait
  sleep 60
done
