#!/bin/bash

# ==========================================================
#   BD-KING-R7 × TAMANNA AI — OMEGA-PLUS POWER ENGINE v3.0
#   Power Fusion • Resonance • Overdrive • Stabilization
# ==========================================================

ROOT="$HOME/tamanna"
LOG="$ROOT/bd_king_r7_power_omega.log"
STATE="$ROOT/bd_king_r7_state.db"
TIME=$(date +"%Y-%m-%d %H:%M:%S")

mkdir -p "$ROOT"

echo "==================================================" >> "$LOG"
echo "⚡ BD-KING-R7 OMEGA-PLUS POWER ENGINE — $TIME" >> "$LOG"
echo "==================================================" >> "$LOG"

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
    echo "power_mode=SUPERSONIC" > "$STATE"
    echo "power_history=0" >> "$STATE"
    echo "power_drift=0" >> "$STATE"
    echo "power_stability=100" >> "$STATE"
fi

# ----------------------------------------------------------
#  POWER TABLE (16 MODES)
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
#  POWER FUSION ENGINE
# ----------------------------------------------------------
power_fusion() {
    MODE=$(memory_get "power_mode")
    BASE=$(get_base_power "$MODE")

    # Fusion multiplier (random + drift)
    DRIFT=$(memory_get "power_drift")
    FUSION=$(( (RANDOM % 20) + DRIFT + 100 ))
    POWER=$(( BASE * FUSION / 100 ))

    echo "🔱 Power Fusion: ${FUSION}% → $POWER W" >> "$LOG"
    echo "$POWER"
}

# ----------------------------------------------------------
#  POWER DRIFT ENGINE
# ----------------------------------------------------------
power_drift() {
    DRIFT=$(memory_get "power_drift")

    # Drift increases with high power modes
    MODE=$(memory_get "power_mode")
    case "$MODE" in
        VOID_CROWN|AETHER_FLOW|TEMPEST_ASCENT|MAGMA_FORGE)
            DRIFT=$((DRIFT + 3))
            ;;
        OMEGA_ASCEND|QUANTUM_VOID|INFERNO_DRIVE)
            DRIFT=$((DRIFT + 2))
            ;;
        *)
            DRIFT=$((DRIFT + 1))
            ;;
    esac

    # Drift soft cap
    (( DRIFT > 50 )) && DRIFT=50

    memory_set "power_drift" "$DRIFT"
    echo "🌀 Power Drift: $DRIFT" >> "$LOG"
}

# ----------------------------------------------------------
#  POWER STABILITY ENGINE
# ----------------------------------------------------------
power_stability() {
    STAB=$(memory_get "power_stability")
    DRIFT=$(memory_get "power_drift")

    # Stability decreases with drift
    STAB=$((STAB - (DRIFT / 5)))

    # Random instability
    STAB=$((STAB - (RANDOM % 3)))

    # Clamp
    (( STAB < 0 )) && STAB=0
    (( STAB > 100 )) && STAB=100

    memory_set "power_stability" "$STAB"
    echo "🧩 Power Stability: $STAB%" >> "$LOG"

    echo "$STAB"
}

# ----------------------------------------------------------
#  POWER SURGE / COLLAPSE ENGINE
# ----------------------------------------------------------
power_event() {
    STAB=$(memory_get "power_stability")

    if (( STAB < 20 )); then
        echo "⚠️ POWER COLLAPSE DETECTED" >> "$LOG"
        echo "   → Switching to EARTH_HEART (stabilizer)" >> "$LOG"
        memory_set "power_mode" "EARTH_HEART"
        memory_set "power_stability" 80
        return
    fi

    if (( STAB > 90 )); then
        echo "✨ POWER SURGE ACTIVATED" >> "$LOG"
        echo "   → Switching to VOID_CROWN (max tier)" >> "$LOG"
        memory_set "power_mode" "VOID_CROWN"
    fi
}

# ----------------------------------------------------------
#  MAIN POWER CYCLE
# ----------------------------------------------------------
MODE=$(memory_get "power_mode")
echo "⚡ Current Mode: $MODE" >> "$LOG"

power_drift
STAB=$(power_stability)
power_event
POWER=$(power_fusion)

echo "✅ OMEGA-PLUS Power Cycle Complete — $TIME" >> "$LOG"
echo "" >> "$LOG"
