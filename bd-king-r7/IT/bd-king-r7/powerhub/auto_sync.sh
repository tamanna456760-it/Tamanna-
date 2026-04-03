#!/bin/bash

REPO_DIR="$HOME/tamanna-system"
LOG_FILE="$REPO_DIR/powerhub_sync.log"

cd "$REPO_DIR" || exit 1

echo "===== PowerHub Auto Sync =====" >> "$LOG_FILE"
date >> "$LOG_FILE"

git reset --hard HEAD >> "$LOG_FILE" 2>&1
git pull origin main >> "$LOG_FILE" 2>&1

echo "✔ Sync completed" >> "$LOG_FILE"