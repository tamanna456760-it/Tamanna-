#!/bin/bash

# ==========================================================
#   BD-KING-R7 × TAMANNA AI — SERVER PULSE ENGINE v1.0
#   Connects to bd-king-r7.io and logs server heartbeat
# ==========================================================

ROOT="$HOME/tamanna"
LOG="$ROOT/tamanna_server_pulse.log"
TIME=$(date +"%Y-%m-%d %H:%M:%S")

mkdir -p "$ROOT"

SERVER="${BD_KING_R7_SERVER:-bd-king-r7.io}"
USER="$BD_KING_R7_USER"
PASS="$BD_KING_R7_PASS"

echo "==================================================" >> "$LOG"
echo "🌐 Tamanna Server Pulse — $TIME" >> "$LOG"
echo "==================================================" >> "$LOG"

# ----------------------------------------------------------
#  CHECK CREDENTIALS
# ----------------------------------------------------------
if [ -z "$USER" ] || [ -z "$PASS" ]; then
    echo "⚠️ Missing BD_KING_R7_USER or BD_KING_R7_PASS env vars" >> "$LOG"
    echo "❌ Server Pulse Aborted" >> "$LOG"
    echo "" >> "$LOG"
    exit 1
fi

# ----------------------------------------------------------
#  SERVER PULSE REQUEST (HTTP EXAMPLE)
#  Adjust endpoint according to your server API
# ----------------------------------------------------------

PULSE_URL="https://$SERVER/api/pulse"

echo "📡 Sending pulse request to $PULSE_URL" >> "$LOG"

RESPONSE=$(curl -s -u "$USER:$PASS" "$PULSE_URL")

if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
    echo "❌ Pulse Failed → No response or connection error" >> "$LOG"
    echo "" >> "$LOG"
    exit 1
fi

echo "✅ Pulse Response: $RESPONSE" >> "$LOG"

# ----------------------------------------------------------
#  OPTIONAL: PARSE RESPONSE (JSON-LIKE)
#  You can customize this depending on your server output
# ----------------------------------------------------------
if echo "$RESPONSE" | grep -qi "OK"; then
    echo "💓 Server Status: ALIVE" >> "$LOG"
else
    echo "⚠️ Server Status: UNKNOWN / NON-OK" >> "$LOG"
fi

echo "✅ Server Pulse Cycle Complete — $TIME" >> "$LOG"
echo "" >> "$LOG"
