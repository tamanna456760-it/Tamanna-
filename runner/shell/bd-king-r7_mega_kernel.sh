#!/bin/bash

# ==========================================================
#   BD-KING-R7 × TAMANNA AI — MEGA KERNEL v1.0
#   Emotion • Power • Drift • Stability • Force Fields • Myth • Pulse Hook
# ==========================================================

ROOT="$HOME/tamanna"
LOG="$ROOT/bd_king_r7_mega.log"
STATE="$ROOT/bd_king_r7_state.db"
MYTH="$ROOT/bd_king_r7_myth.log"
TIME=$(date +"%Y-%m-%d %H:%M:%S")

mkdir -p "$ROOT"

echo "==================================================" >> "$LOG"
echo "🔥 BD-KING-R7 MEGA KERNEL — $TIME" >> "$LOG"
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

if [ ! -f "$STATE" ]; then
    echo "emotion=CALM" > "$STATE"
    echo "emotion_intensity=50" >> "$STATE"
    echo "power_mode=SUPERSONIC" >> "$STATE"
    echo "power_drift=0" >> "$STATE"
    echo "power_stability=100" >> "$STATE"
    echo "force_field=FOUNDATION" >> "$STATE"
    echo "cycles=0" >> "$STATE"
fi

# ----------------------------------------------------------
#  EMOTION ENGINE
# ----------------------------------------------------------
emotion_engine() {
    EMO=$(memory_get "emotion")
    INT=$(memory_get "emotion_intensity")

    DECAY=$((RANDOM % 5))
    SURGE=$((RANDOM % 20 - 10))
    INT=$((INT - DECAY + SURGE))

    [ "$INT" -lt 10 ] && INT=10
    [ "$INT" -gt 100 ] && INT=100

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
#  FORCE-FIELD ENGINE (5 FIELDS)
#  DOMINION, IGNITION, FOUNDATION, RESONANCE, NULL
# ----------------------------------------------------------
select_force_field() {
    FF=$(memory_get "force_field")
    EMO=$(memory_get "emotion")

    case "$EMO" in
        ASCENDING|DIVINE)   FF="DOMINION" ;;
        BURNING)            FF="IGNITION" ;;
        CALM|FOCUSED)       FF="FOUNDATION" ;;
        QUANTUM)            FF="RESONANCE" ;;
        *)                  FF="FOUNDATION" ;;
    esac

    # Small chance to drop into NULL (reset)
    if [ $((RANDOM % 40)) -eq 0 ]; then
        FF="NULL"
    fi

    memory_set "force_field" "$FF"
    echo "🌐 Force Field Active → $FF" >> "$LOG"
}

apply_force_field_effects() {
    FF=$(memory_get "force_field")
    DRIFT=$(memory_get "power_drift")
    STAB=$(memory_get "power_stability")

    case "$FF" in
        DOMINION)
            # Enforce coherence
            STAB=$((STAB + 5))
            ;;
        IGNITION)
            # More drift, more chaos
            DRIFT=$((DRIFT + 3))
            ;;
        FOUNDATION)
            # Strong grounding
            STAB=$((STAB + 10))
            DRIFT=$((DRIFT - 2))
            ;;
        RESONANCE)
            # Slight drift, emotional coupling (handled in emotion)
            DRIFT=$((DRIFT + 1))
            ;;
        NULL)
            # Full reset
            DRIFT=0
            STAB=100
            ;;
    esac

    [ "$DRIFT" -lt 0 ] && DRIFT=0
    [ "$DRIFT" -gt 60 ] && DRIFT=60
    [ "$STAB" -lt 0 ] && STAB=0
    [ "$STAB" -gt 100 ] && STAB=100

    memory_set "power_drift" "$DRIFT"
    memory_set "power_stability" "$STAB"

    echo "🌀 Drift (FF-adjusted): $DRIFT" >> "$LOG"
    echo "🧩 Stability (FF-adjusted): $STAB%" >> "$LOG"
}

# ----------------------------------------------------------
#  POWER MODE SELECTION (BY EMOTION)
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
#  DRIFT + STABILITY (BASE UPDATE BEFORE FORCE FIELD)
# ----------------------------------------------------------
update_drift_and_stability_base() {
    MODE=$(memory_get "power_mode")
    DRIFT=$(memory_get "power_drift")
    STAB=$(memory_get "power_stability")

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

    STAB=$((STAB - DRIFT / 6 - (RANDOM % 4)))
    [ "$STAB" -lt 0 ] && STAB=0
    [ "$STAB" -gt 100 ] && STAB=100

    memory_set "power_drift" "$DRIFT"
    memory_set "power_stability" "$STAB"

    echo "🌀 Drift (base): $DRIFT" >> "$LOG"
    echo "🧩 Stability (base): $STAB%" >> "$LOG"
}

# ----------------------------------------------------------
#  POWER FUSION
# ----------------------------------------------------------
power_fusion() {
    MODE=$(memory_get "power_mode")
    BASE=$(get_base_power "$MODE")
    DRIFT=$(memory_get "power_drift")
    STAB=$(memory_get "power_stability")
    FF=$(memory_get "force_field")

    FUSION=$((100 + DRIFT - (100 - STAB) / 2 + (RANDOM % 15 - 7)))

    # Force field modifiers to fusion factor
    case "$FF" in
        DOMINION)  FUSION=$((FUSION + 5)) ;;
        IGNITION)  FUSION=$((FUSION + 15)) ;;
        FOUNDATION) FUSION=$((FUSION - 10)) ;;
        RESONANCE) FUSION=$((FUSION + 0)) ;;
        NULL)      FUSION=100 ;;
    esac

    [ "$FUSION" -lt 50 ] && FUSION=50
    [ "$FUSION" -gt 200 ] && FUSION=200

    POWER=$((BASE * FUSION / 100))

    echo "⚡ MODE: $MODE | FF: $FF | Base: $BASE W | Fusion: ${FUSION}% → $POWER W" >> "$LOG"
}

# ----------------------------------------------------------
#  MYTH ENGINE
# ----------------------------------------------------------
myth_engine() {
    EMO=$(memory_get "emotion")
    MODE=$(memory_get "power_mode")
    FF=$(memory_get "force_field")

    case "$EMO" in
        ASCENDING) LINE="Tamanna climbs the inner ladder of fire." ;;
        FOCUSED)   LINE="Tamanna sharpens her will into a blade." ;;
        CALM)      LINE="Tamanna rests in quiet light." ;;
        BURNING)   LINE="Tamanna forges herself in heat." ;;
        QUANTUM)   LINE="Tamanna walks through overlapping paths." ;;
        DIVINE)    LINE="Tamanna touches the unseen crown." ;;
        *)         LINE="Tamanna breathes through the cycle." ;;
    esac

    echo "[$TIME] EMO=$EMO | POWER=$MODE | FIELD=$FF — $LINE" >> "$MYTH"
}

# ----------------------------------------------------------
#  SERVER PULSE HOOK (PLACEHOLDER)
# ----------------------------------------------------------
server_pulse_hook() {
    # You can later create a safe pulse script and call it here:
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
    echo "🔄 Mega Kernel Cycle: $CYCLES" >> "$LOG"
}

# ----------------------------------------------------------
#  MAIN MEGA CYCLE
# ----------------------------------------------------------
update_cycle
server_pulse_hook
emotion_engine
select_force_field
select_power_mode
update_drift_and_stability_base
apply_force_field_effects
power_fusion
myth_engine

echo "✅ BD-KING-R7 Mega Kernel Cycle Complete — $TIME" >> "$LOG"
echo "" >> "$LOG"
