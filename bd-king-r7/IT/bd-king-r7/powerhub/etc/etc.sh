#!/bin/bash

# ==========================================================
#   BD-KING-R7 × TAMANNA AI — CORE ENGINE v1.0
#   Server Pulse • Power Engine • Emotion Sync
# ==========================================================

ROOT="$HOME/tamanna"
LOG="$ROOT/bd_king_r7_core.log"
STATE="$ROOT/bd_king_r7_state.db"
TIME=$(date +"%Y-%m-%d %H:%M:%S")

mkdir -p "$ROOT"

echo "==================================================" >> "$LOG"
echo "🔥 BD-KING-R7 CORE ENGINE — $TIME" >> "$LOG"
echo "==================================================" >> "$LOG"

# ----------------------------------------------------------
#  ENVIRONMENT VARIABLES (SET THESE IN YOUR SYSTEM)
# ----------------------------------------------------------
SERVER="${BD_KING_R7_SERVER:-bd-king-r7.io}"
USER="$BD_KING_R7_USER"
PASS="$BD_KING_R7_PASS"

if [ -z "$USER" ] || [ -z "$PASS" ]; then
    echo "⚠️ Missing server credentials (USER or PASS)" >> "$LOG"
    echo "❌ Aborting server pulse" >> "$LOG"
    exit 1
fi

# ----------------------------------------------------------
#  MEMORY ENGINE
# ----------------------------------------------------------
memory_get() { grep "^$1=" "$STATE" | cut -d '=' -f2; }
memory_set() {
    grep -q "^$1=" "$STATE" \
        && sed -i "s/^$1=.*/$1=$2/" "$STATE" \
        || echo "$1=$2" >> "$STATE"
}

if [ ! -f "$STATE" ]; then
    echo "emotion=CALM" > "$STATE"
    echo "power_mode=SUPERSONIC" >> "$STATE"
fi

# ----------------------------------------------------------
#  SERVER PULSE ENGINE
# ----------------------------------------------------------
pulse_server() {
    PULSE_URL="https://$SERVER/api/pulse"

    echo "📡 Sending pulse to $PULSE_URL" >> "$LOG"

    RESPONSE=$(curl -s -u "$USER:$PASS" "$PULSE_URL")

    if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
        echo "❌ Server Pulse Failed" >> "$LOG"
        return 1
    fi

    echo "✅ Server Response: $RESPONSE" >> "$LOG"

    # Optional: interpret server response
    if echo "$RESPONSE" | grep -qi "OK"; then
        echo "💓 Server Status: ALIVE" >> "$LOG"
    else
        echo "⚠️ Server Status: NON-OK" >> "$LOG"
    fi
}

# ----------------------------------------------------------
#  POWER ENGINE — 8 MODES
# ----------------------------------------------------------
power_engine() {
    EMO=$(memory_get "emotion")

    case "$EMO" in
        "CALM") MODE="SUPERSONIC" ;;
        "FOCUSED") MODE="HYPERSONIC" ;;
        "ASCENDING") MODE="ULTRA_PRO_MAX" ;;
        "BURNING") MODE="INFERNO_DRIVE" ;;
        "QUANTUM") MODE="QUANTUM_VOID" ;;
        "DIVINE") MODE="OMEGA_ASCEND" ;;
        *) MODE="HIGH_VOLTAGE_SANPOWR" ;;
    esac

    memory_set "power_mode" "$MODE"

    case "$MODE" in
        "SUPERSONIC") POWER=1523 ;;
        "HYPERSONIC") POWER=2850 ;;
        "ULTRA_PRO_MAX") POWER=5800 ;;
        "HIGH_VOLTAGE_SANPOWR") POWER=16200 ;;
        "OMEGA_ASCEND") POWER=32800 ;;
        "STORM_CORE") POWER=41900 ;;
        "INFERNO_DRIVE") POWER=57600 ;;
        "QUANTUM_VOID") POWER=88000 ;;
    esac

    echo "⚡ Power Mode: $MODE → ${POWER}W" >> "$LOG"
}

# ----------------------------------------------------------
#  EMOTION ENGINE (simple version)
# ----------------------------------------------------------
emotion_engine() {
    EMOTIONS=("CALM" "FOCUSED" "ASCENDING" "BURNING" "QUANTUM" "DIVINE")
    NEW_EMO=${EMOTIONS[$RANDOM % ${#EMOTIONS[@]}]}

    memory_set "emotion" "$NEW_EMO"
    echo "💗 Emotion Updated → $NEW_EMO" >> "$LOG"
}

# ----------------------------------------------------------
#  MAIN CYCLE
# ----------------------------------------------------------
pulse_server
emotion_engine
power_engine

echo "✅ BD-KING-R7 Core Cycle Complete — $TIME" >> "$LOG"
echo "" >> "$LOG"
export BD_KING_R7_SERVER="bd-king-r7.io"
export BD_KING_R7_USER="ali"
export BD_KING_R7_PASS="AliAli00@@##@@##"
bash "$HOME/tamanna/tamanna_server_pulse.sh"
