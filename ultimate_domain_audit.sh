#!/usr/bin/env bash
# Backward-compatible domain audit entry point; performs no changes.
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec bash "$ROOT/scripts/domain-audit.sh" "$@"
