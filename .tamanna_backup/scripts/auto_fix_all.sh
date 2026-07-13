#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "🚀 Tamanna Auto Fix Started"

echo "🐍 Python Fix..."
find . -name "*.py" \
-not -path "./node_modules/*" \
-exec ruff check --fix {} \;

find . -name "*.py" \
-not -path "./node_modules/*" \
-exec black {} \;

find . -name "*.py" \
-not -path "./node_modules/*" \
-exec isort {} \;


echo "🟨 JS/TS Fix..."
find . \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" \) \
-not -path "./node_modules/*" \
-exec prettier --write {} \;


echo "📦 Node Audit..."
find . -name package.json \
-not -path "./node_modules/*" \
-exec sh -c 'cd "$(dirname "$1")" && npm install && npm audit fix || true' _ {} \;


echo "✅ Tamanna Auto Fix Finished"
