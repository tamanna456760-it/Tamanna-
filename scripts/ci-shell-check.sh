#!/usr/bin/env bash
# Tamanna AI CI shell bootstrap and read-only health check.
# Runs only inside the disposable GitHub Actions runner.
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

echo "=== Tamanna AI Shell Environment ==="
printf 'User: '; id -un
printf 'OS: '; . /etc/os-release && echo "$PRETTY_NAME"
printf 'Kernel: '; uname -sr
printf 'Bash: %s\n' "$BASH_VERSION"
printf 'Python: '; python3 --version
printf 'Git: '; git --version

echo "=== Repository checks (read-only) ==="
git status --short
python3 - <<'PY'
from pathlib import Path
root = Path(".")
required = ["README.md"]
missing = [name for name in required if not (root / name).exists()]
if missing:
    print("Missing expected files:", ", ".join(missing))
    raise SystemExit(1)
print("Repository structure check: PASS")
PY

if command -v shellcheck >/dev/null 2>&1; then
  echo "=== ShellCheck ==="
  find scripts -type f -name '*.sh' -print0 2>/dev/null |
    xargs -0 -r shellcheck
else
  echo "ShellCheck not installed; syntax-checking tracked shell scripts."
  while IFS= read -r -d '' file; do
    bash -n "$file"
    echo "Syntax OK: $file"
  done < <(find scripts -type f -name '*.sh' -print0 2>/dev/null || true)
fi

echo "Tamanna CI shell check completed."
