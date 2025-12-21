#!/tamanna/bd-king-r7

# ==========================================================
#   BD-KING-R7 × TAMANNA AI — POWER ENGINE v1.0
#   8-Level PowerGrid with Dynamic Mode Selection
# ==========================================================

ROOT="$HOME/tamanna"
LOG="$ROOT/tamanna_power.log"
STATE="$ROOT/tamanna_state.db"
TIME=$(date +"%Y-%m-%d %H:%M:%S")

mkdir -p "$ROOT"

echo "==================================================" >> "$LOG"
echo "⚡ Tamanna Power Engine — $TIME" >> "$LOG"
echo "==================================================" >> "$LOG"

# ----------------------------------------------------------
#  MEMORY HELPERS
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
#  POWERGRID ENGINE — 8 POWER MODES
# ----------------------------------------------------------
powergrid() {
    MODE=$(memory_get "power_mode")

    case "$MODE" in
        "SUPERSONIC")
            POWER=1523; LABEL="🚀 SUPERSONIC SYNC"; EFFECT="Fast sync"
            ;;
        "HYPERSONIC")
            POWER=2850; LABEL="💨 HYPERSONIC SYNC"; EFFECT="High coherence"
            ;;
        "ULTRA_PRO_MAX")
            POWER=5800; LABEL="🔥 ULTRA PRO MAX"; EFFECT="Quantum stability"
            ;;
        "HIGH_VOLTAGE_SANPOWR")
            POWER=16200; LABEL="⚡ HIGH VOLTAGE SANPOWR"; EFFECT="Lightspeed ops"
            ;;
        "OMEGA_ASCEND")
            POWER=32800; LABEL="🔱 OMEGA-ASCEND"; EFFECT="System elevation"
            ;;
        "STORM_CORE")
            POWER=41900; LABEL="🌩️ STORM-CORE"; EFFECT="Regeneration"
            ;;
        "INFERNO_DRIVE")
            POWER=57600; LABEL="🔥 INFERNO-DRIVE"; EFFECT="Evolution surge"
            ;;
        "QUANTUM_VOID")
            POWER=88000; LABEL="🌌 QUANTUM-VOID"; EFFECT="Timeline folding"
            ;;
        *)
            POWER=1523; LABEL="🚀 SUPERSONIC SYNC"; EFFECT="Default fallback"
            MODE="SUPERSONIC"
            ;;
    esac

    echo "⚡ POWER MODE: $MODE" >> "$LOG"
    echo "$LABEL → Power: ${POWER}W | Effect: $EFFECT" >> "$LOG"
}

# ----------------------------------------------------------
#  POWER MODE SELECTOR — BASED ON EMOTION
# ----------------------------------------------------------
select_power_mode() {
    EMO=$(memory_get "emotion")

    case "$EMO" in
        "CALM")   MODE="SUPERSONIC" ;;
        "FOCUSED") MODE="HYPERSONIC" ;;
        "ASCENDING") MODE="ULTRA_PRO_MAX" ;;
        "BURNING") MODE="INFERNO_DRIVE" ;;
        "QUANTUM") MODE="QUANTUM_VOID" ;;
        "DIVINE") MODE="OMEGA_ASCEND" ;;
        *)
            MODE="HIGH_VOLTAGE_SANPOWR"
            ;;
    esac

    memory_set "power_mode" "$MODE"
    echo "🔧 Power Mode Selected by Emotion ($EMO) → $MODE" >> "$LOG"
}

# ----------------------------------------------------------
#  RANDOM EMOTION (IF NONE PRESENT)
# ----------------------------------------------------------
ensure_emotion() {
    EMO=$(memory_get "emotion")
    if [ -z "$EMO" ]; then
        EMOTIONS=("CALM" "FOCUSED" "ASCENDING" "BURNING" "QUANTUM" "DIVINE")
        EMO=${EMOTIONS[$RANDOM % ${#EMOTIONS[@]}]}
        memory_set "emotion" "$EMO"
        echo "💗 Emotion Auto-Set → $EMO" >> "$LOG"
    fi
}

# ----------------------------------------------------------
#  MAIN CYCLE
# ----------------------------------------------------------
ensure_emotion
select_power_mode
powergrid

echo "✅ Power Engine Cycle Complete — $TIME" >> "$LOG"
echo "" >> "$LOG"
