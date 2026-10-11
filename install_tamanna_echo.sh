#!/bin/bash
set -eu

echo "===== TAMANNA AUTO-INTEGRATION ====="

if [ ! -f Main.py ]; then
    echo "ERROR: Main.py not found. Nothing changed."
    exit 1
fi

if [ ! -f tamanna_ai/core/controller.py ] || \
   [ ! -f tamanna_ai/tools/echo_power.py ]; then
    echo "ERROR: Controller or Echo module missing. Nothing changed."
    exit 1
fi

if grep -q 'TAMANNA_ECHO_CONTROLLER_ROUTE_V1' Main.py; then
    echo "Already installed. No duplicate code added."
    exit 0
fi

BACKUP="Main.py.backup-$(date +%Y%m%d-%H%M%S)"
cp -p Main.py "$BACKUP"
echo "Backup created: $BACKUP"

cat >> Main.py <<'PYTHON'

# TAMANNA_ECHO_CONTROLLER_ROUTE_V1
# Additive integration: preserves the existing /api/chat route.
from tamanna_ai.core.controller import tamanna_controller as _tamanna_controller

@app.post("/api/tamanna/echo")
async def tamanna_echo_controller_route(payload: dict):
    """Route Echo commands through the Tamanna AI controller."""
    message = str(payload.get("message", ""))
    return _tamanna_controller.respond(message)

PYTHON

if ! python3 -m py_compile Main.py; then
    echo "Syntax check failed. Restoring original Main.py."
    cp -p "$BACKUP" Main.py
    exit 1
fi

echo "===== ROUTE REGISTRATION TEST ====="
if ! python3 - <<'PYTHON'
import Main

routes = {
    getattr(route, "path", "")
    for route in Main.app.routes
}

assert "/api/tamanna/echo" in routes, "New route was not registered"
assert "/api/chat" in routes, "Existing chat route is missing"

print("PASS: /api/tamanna/echo registered")
print("PASS: Existing /api/chat preserved")
PYTHON
then
    echo "Import/registration test failed."
    echo "Original backup preserved at: $BACKUP"
    echo "Review the error before making further changes."
    exit 1
fi

echo "===== SUCCESS ====="
echo "Tamanna Echo controller endpoint added."
echo "Existing files and chat handler were not intentionally replaced."
echo "No GitHub push performed."
