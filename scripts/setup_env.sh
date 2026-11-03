#!/usr/bin/env bash
# Create a private local .env from the safe template without overwriting secrets.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -e .env ]]; then
  echo ".env already exists; leaving it unchanged."
  exit 0
fi
if [[ ! -f .env.example ]]; then
  echo "ERROR: .env.example is missing." >&2
  exit 1
fi
umask 077
cp .env.example .env
chmod 600 .env
echo "Created private .env from .env.example."
echo "Add your real GEMINI_API_KEY and a unique TAMANNA_SESSION_SECRET locally."
