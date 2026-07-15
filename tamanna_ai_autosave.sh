#!/data/data/com.termux/files/usr/bin/bash
set -e

REPO="$HOME/tamanna-"
BRANCH="main"

cd "$REPO"

echo "=== Tamanna AI Auto Save ==="
echo "Time: $(date)"

# Git status
git status

# Python syntax check (if any)
find . -name "*.py" -print0 | while IFS= read -r -d '' f; do
    python -m py_compile "$f" || true
done

# Optional formatting tools (run only if installed)
command -v ruff >/dev/null && ruff check --fix . || true
command -v black >/dev/null && black . || true
command -v isort >/dev/null && isort . || true

# Optional tests
[ -d tests ] && python -m pytest || true

# Save to GitHub
git add -A

if ! git diff --cached --quiet; then
    git commit -m "Tamanna AI Auto Save $(date '+%F %T')" || true
    git pull --rebase origin "$BRANCH" || true
    git push origin "$BRANCH"
else
    echo "No changes to commit."
fi

echo "Done."
