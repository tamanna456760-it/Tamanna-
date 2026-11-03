#!/usr/bin/env bash
# Non-destructive validation used by the Makefile "fix" target.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v python3 >/dev/null 2>&1 || {
  echo "ERROR: python3 is required." >&2
  exit 127
}
command -v bash >/dev/null 2>&1 || {
  echo "ERROR: bash is required." >&2
  exit 127
}

echo "[Tamanna] Checking main Python entry points..."
python3 -m py_compile Main.py main.py

echo "[Tamanna] Checking repaired shell entry points..."
bash -n runner/shell/tamanna_ai.sh
bash -n runner/shell/cak.sh

echo "[Tamanna] Validation complete. No files were rewritten."
