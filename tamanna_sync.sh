#!/data/data/com.termux/files/usr/bin/bash

REPO="$HOME/tamanna-"

cd "$REPO" || exit 1

echo "[Tamanna AI] Sync Started: $(date)"

git add -A

if ! git diff --cached --quiet; then
    git commit -m "Tamanna AI Auto Sync - $(date '+%Y-%m-%d %H:%M:%S')"
    git pull --rebase origin main
    git push origin main
else
    echo "No changes detected."
fi

echo "[Tamanna AI] Sync Complete."
