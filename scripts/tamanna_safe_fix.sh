#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "🛡️ Tamanna Safe Auto Fix"

# Backup
mkdir -p .tamanna_backup

git ls-files | while read file; do
    if [ -f "$file" ]; then
        cp --parents "$file" .tamanna_backup/
    fi
done

echo "✅ Backup completed"

# Python fix
find . -name "*.py" \
-not -path "./node_modules/*" \
-exec python -m compileall {} \; || true

# JSON check
find . -name "*.json" \
-not -path "./node_modules/*" \
-exec python -m json.tool {} \; || true

# JS format
if command -v prettier >/dev/null; then
find . \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" \) \
-not -path "./node_modules/*" \
-exec prettier --write {} \;
fi

echo "✅ Fix completed"
