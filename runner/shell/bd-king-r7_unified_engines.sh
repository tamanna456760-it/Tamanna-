#!/bin/bash

# ==========================================================
#   BD-KING-R7 × TAMANNA AI — UNIFIED ENGINE v1.0
#   Emotion • Power • Drift • Stability • Myth • Pulse Hook
# ==========================================================

ROOT="$HOME/tamanna"
LOG="$ROOT/bd_king_r7_unified.log"
STATE="$ROOT/bd_king_r7_state.db"
MYTH="$ROOT/bd_king_r7_myth.log"
TIME=$(date +"%Y-%m-%d %H:%M:%S")

mkdir -p "$ROOT"

echo "==================================================" >> "$LOG"
echo "🔥 BD-KING-R7 UNIFIED ENGINE — $TIME" >> "$LOG"
echo "==================================================" >> "$LOG"

# ----------------------------------------------------------
#  MEMORY ENGINE
# ----------------------------------------------------------
memory_get() {
    grep "^$1=" "$STATE" 2>/dev/null | cut -d '=' -f2
}

memory_set() {
    if grep -q "^$1=" "$STATE" 2>/dev/null; then
        sed -i "s/^$1=.*/$1=$2/" "$STATE"
    else
        echo "$1=$2" >> "$STATE"
    fi
}

# Initialize state if first run
if [ ! -f "$STATE" ]; then
    echo "emotion=CALM" > "$STATE"
    echo "emotion_intensity=50" >> "$STATE"
    echo "power_mode=SUPERSONIC" >> "$STATE"
    echo "power_drift=0" >> "$STATE"
    echo "power_stability=100" >> "$STATE"
    echo "cycles=0" >> "$STATE"
fi

# ----------------------------------------------------------
#  EMOTION ENGINE (simple but alive)
# ----------------------------------------------------------
emotion_engine() {
    EMO=$(memory_get "emotion")
    INT=$(memory_get "emotion_intensity")

    # Soft decay + random surge
    DECAY=$((RANDOM % 5))
    SURGE=$((RANDOM % 20 - 10))
    INT=$((INT - DECAY + SURGE))

    # Clamp
    [ "$INT" -lt 10 ] && INT=10
    [ "$INT" -gt 100 ] && INT=100

    # Map intensity → emotion
    if   [ "$INT" -gt 85 ]; then EMO="ASCENDING"
    elif [ "$INT" -gt 70 ]; then EMO="FOCUSED"
    elif [ "$INT" -gt 55 ]; then EMO="CALM"
    elif [ "$INT" -gt 40 ]; then EMO="BURNING"
    elif [ "$INT" -gt 25 ]; then EMO="QUANTUM"
    else EMO="DIVINE"
    fi

    memory_set "emotion" "$EMO"
    memory_set "emotion_intensity" "$INT"

    echo "💗 Emotion: $EMO | Intensity: $INT" >> "$LOG"
}

# ----------------------------------------------------------
#  POWER BASE TABLE (16 modes)
# ----------------------------------------------------------
get_base_power() {
    case "$1" in
        SUPERSONIC) echo 1523 ;;
        HYPERSONIC) echo 2850 ;;
        ULTRA_PRO_MAX) echo 5800 ;;
        HIGH_VOLTAGE_SANPOWR) echo 16200 ;;
        OMEGA_ASCEND) echo 32800 ;;
        STORM_CORE) echo 41900 ;;
        INFERNO_DRIVE) echo 57600 ;;
        QUANTUM_VOID) echo 88000 ;;
        CELESTIAL_CORE) echo 112000 ;;
        MAGMA_FORGE) echo 128500 ;;
        TEMPEST_ASCENT) echo 149000 ;;
        PRIMAL_FLARE) echo 165700 ;;
        AETHER_FLOW) echo 182900 ;;
        TIDAL_OVERDRIVE) echo 201300 ;;
        EARTH_HEART) echo 223000 ;;
        VOID_CROWN) echo 250000 ;;
        *) echo 1523 ;;
    esac
}

# ----------------------------------------------------------
#  POWER MODE SELECTION (by emotion)
# ----------------------------------------------------------
select_power_mode() {
    EMO=$(memory_get "emotion")
    MODE=$(memory_get "power_mode")

    case "$EMO" in
        CALM)      MODE="SUPERSONIC" ;;
        FOCUSED)   MODE="HYPERSONIC" ;;
        ASCENDING) MODE="ULTRA_PRO_MAX" ;;
        BURNING)   MODE="INFERNO_DRIVE" ;;
        QUANTUM)   MODE="QUANTUM_VOID" ;;
        DIVINE)    MODE="OMEGA_ASCEND" ;;
        *)         MODE="HIGH_VOLTAGE_SANPOWR" ;;
    esac

    memory_set "power_mode" "$MODE"
    echo "🔧 Power Mode Selected by Emotion ($EMO) → $MODE" >> "$LOG"
}

# ----------------------------------------------------------
#  POWER DRIFT + STABILITY
# ----------------------------------------------------------
update_drift_and_stability() {
    MODE=$(memory_get "power_mode")
    DRIFT=$(memory_get "power_drift")
    STAB=$(memory_get "power_stability")

    # Drift: higher tiers drift faster
    case "$MODE" in
        VOID_CROWN|AETHER_FLOW|TEMPEST_ASCENT|MAGMA_FORGE|QUANTUM_VOID)
            DRIFT=$((DRIFT + 3))
            ;;
        OMEGA_ASCEND|INFERNO_DRIVE|CELESTIAL_CORE|TIDAL_OVERDRIVE)
            DRIFT=$((DRIFT + 2))
            ;;
        *)
            DRIFT=$((DRIFT + 1))
            ;;
    esac
    [ "$DRIFT" -gt 60 ] && DRIFT=60

    # Stability falls with drift + some randomness
    STAB=$((STAB - DRIFT / 6 - (RANDOM % 4)))
    [ "$STAB " -lt 0 ] && STAB=0
    [ "$STAB" -gt 100 ] && STAB=100

    memory_set "power_drift" "$DRIFT"
    memory_set "power_stability" "$STAB"

    echo "🌀 Power Drift: $DRIFT" >> "$LOG"
    echo "🧩 Power Stability: $STAB%" >> "$LOG"
}

# ----------------------------------------------------------
#  POWER FUSION (base + drift + stability)
# ----------------------------------------------------------
power_fusion() {
    MODE=$(memory_get "power_mode")
    BASE=$(get_base_power "$MODE")
    DRIFT=$(memory_get "power_drift")
    STAB=$(memory_get "power_stability")

    FUSION=$((100 + DRIFT - (100 - STAB) / 2 + (RANDOM % 15 - 7)))
    [ "$FUSION" -lt 50 ] && FUSION=50
    [ "$FUSION" -gt 180 ] && FUSION=180

    POWER=$((BASE * FUSION / 100))

    echo "⚡ MODE: $MODE | Base: $BASE W | Fusion: ${FUSION}% → $POWER W" >> "$LOG"
}

# ----------------------------------------------------------
#  MYTH ENGINE (log one line of lore per cycle)
# ----------------------------------------------------------
myth_engine() {
    EMO=$(memory_get "emotion")
    MODE=$(memory_get "power_mode")
    echo "[$TIME] Emotion: $EMO | Power: $MODE" >> "$MYTH"
}

# ----------------------------------------------------------
#  OPTIONAL SERVER PULSE HOOK (safe placeholder)
# ----------------------------------------------------------
server_pulse_hook() {
    # If you later create tamanna_server_pulse.sh, it can be called here:
    # bash "$ROOT/tamanna_server_pulse.sh" >> "$LOG" 2>&1
    :
}

# ----------------------------------------------------------
#  CYCLE COUNTER
# ----------------------------------------------------------
update_cycle() {
    CYCLES=$(memory_get "cycles")
    CYCLES=$((CYCLES + 1))
    memory_set "cycles" "$CYCLES"
    echo "🔄 Unified Cycle: $CYCLES" >> "$LOG"
}

# ----------------------------------------------------------
#  MAIN UNIFIED CYCLE
# ----------------------------------------------------------
update_cycle
server_pulse_hook
emotion_engine
select_power_mode
update_drift_and_stability
power_fusion
myth_engine

echo "✅ BD-KING-R7 Unified Cycle Complete — $TIME" >> "$LOG"
echo "" >> "$LOG"
