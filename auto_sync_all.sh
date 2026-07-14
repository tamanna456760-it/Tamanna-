#!/usr/bin/env bash

set -e

echo "======================================"
echo "🔄 Tamanna Auto Sync"
echo "======================================"

# Check Git
if ! command -v git >/dev/null 2>&1; then
    echo "❌ Git is not installed."
    exit 1
fi

# Check repository
if [ ! -d ".git" ]; then
    echo "❌ Current directory is not a Git repository."
    exit 1
fi

# Show branch
BRANCH=$(git branch --show-current)
echo "📌 Branch: $BRANCH"

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ No changes to commit."
    exit 0
fi

echo "📦 Staging changes..."
git add .

COMMIT_MSG="Auto Sync: $(date '+%Y-%m-%d %H:%M:%S')"

echo "📝 Creating commit..."
git commit -m "$COMMIT_MSG"

echo "⬆️ Pushing to origin/$BRANCH..."
git push origin "$BRANCH"

echo "======================================"
echo "✅ Sync completed successfully."
echo "======================================"
