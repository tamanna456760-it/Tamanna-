#!/usr/bin/env bash
# Backward-compatible entry point. This script is deliberately read-only.
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec bash "$ROOT/scripts/domain-audit.sh" "$@"
