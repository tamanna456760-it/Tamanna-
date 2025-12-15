#!/bin/bash
cd "$(dirname "$0")/.." || exit 1

git reset --hard HEAD
git pull origin main
echo "✔ PowerHub Sync Completed"