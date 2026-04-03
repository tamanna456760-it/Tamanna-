#!/bin/bash
# Tamanna System Auto Sync Script
# Path: ./sync/auto_sync.sh

GIT_REPO="https://github.com/Tamannna456760-it/bd-king-r7.git"
SYNC_DIR="$(pwd)"

echo "[SYNC] Starting auto-sync..."
cd $SYNC_DIR || exit
git pull $GIT_REPO main
git add .
git commit -m "Auto-sync commit $(date)"
git push $GIT_REPO main
echo "[SYNC] Auto-sync completed at $(date)"