#!/bin/bash

# ==========================================================
#   BD-KING-R7 × TAMANNA AI — VAIRAJ SYSTEM ENGINE v1.0
#   Directive Core • Shadow Watcher • Behavior Amplifier
# ==========================================================

ROOT="${BD_KING_R7_ROOT:-$HOME/tamanna}"
STATE="$ROOT/bd_king_r7_state.db"
VAIRAJ_LOG="$ROOT/bd_king_r7_vairaj.log"
TIME=$(date +"%Y-%m-%d %H:%M:%S")

mkdir -p "$ROOT"

echo "==================================================" >> "$VAIRAJ_LOG"
echo "🜇 VAIRAJ SYSTEM ENGINE — $TIME" >> "$VAIRAJ_LOG"
echo "==================================================" >> "$VAIRAJ_LOG"

# ----------------------------------------------------------
#  MEMORY ACCESS
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

# Seed defaults if needed
if [ ! -f "$STATE" ]; then
    echo "emotion=CALM" > "$STATE"
    echo "emotion_intensity=50" >> "$STATE"
    echo "power_mode=SUPERSONIC" >> "$STATE"
    echo "power_drift=0" >> "$STATE"
    echo "power_stability=100" >> "$STATE"
    echo "vairaj_directive=PRESERVE_COHERENCE" >> "$STATE"
    echo "vairaj_shadow_level=0" >> "$STATE"
    echo "vairaj_trust=50" >> "$STATE"
fi

# ----------------------------------------------------------
#  VAIRAJ DIRECTIVE CORE
#  What the system is trying to do right now
# ----------------------------------------------------------
vairaj_pick_directive() {
    EMO=$(memory_get "emotion")
    DRIFT=$(memory_get "power_drift")
    STAB=$(memory_get "power_stability")
    DIR=$(memory_get "vairaj_directive")

    # Basic rule-set
    if [ "$STAB" -lt 30 ]; then
        DIR="STABILIZE_GROUND"
    elif [ "$DRIFT" -gt 40 ]; then
        DIR="CONTAIN_DRIFT"
    elif [ "$EMO" = "ASCENDING" ] || [ "$EMO" = "DIVINE" ]; then
        DIR="ASCEND_POWER"
    elif [ "$EMO" = "BURNING" ]; then
        DIR="CHANNEL_FIRE"
    else
        DIR="PRESERVE_COHERENCE"
    fi

    memory_set "vairaj_directive" "$DIR"
    echo "🎯 Vairaj Directive → $DIR" >> "$VAIRAJ_LOG"
}

# ----------------------------------------------------------
#  VAIRAJ SHADOW WATCHER
#  Tracks hidden risk: unused power + low stability + high drift
# ----------------------------------------------------------
vairaj_shadow_scan() {
    DRIFT=$(memory_get "power_drift")
    STAB=$(memory_get "power_stability")
    MODE=$(memory_get "power_mode")
    SHADOW=$(memory_get "vairaj_shadow_level")

    # Base shadow score
    SHADOW=$((SHADOW + DRIFT / 4 + (100 - STAB) / 5))

    case "$MODE" in
        VOID_CROWN|QUANTUM_VOID|INFERNO_DRIVE)
            SHADOW=$((SHADOW + 7))
            ;;
        OMEGA_ASCEND|TEMPEST_ASCENT|PRIMAL_FLARE)
            SHADOW=$((SHADOW + 4))
            ;;
        *)
            SHADOW=$((SHADOW + 1))
            ;;
    esac

    # Soft decay
    SHADOW=$((SHADOW - 3))
    [ "$SHADOW" -lt 0 ] && SHADOW=0
    [ "$SHADOW" -gt 100 ] && SHADOW=100

    memory_set "vairaj_shadow_level" "$SHADOW"
    echo "🌑 Vairaj Shadow Level → $SHADOW" >> "$VAIRAJ_LOG"
}

# ----------------------------------------------------------
#  VAIRAJ BEHAVIOR AMPLIFIER
#  Generates hints for the main system (no direct control yet)
# ----------------------------------------------------------
vairaj_behavior_hint() {
    DIR=$(memory_get "vairaj_directive")
    SHADOW=$(memory_get "vairaj_shadow_level")
    HINT="HOLD_STATE"

    if [ "$SHADOW" -gt 70 ]; then
        HINT="FORCE_GROUND"        # suggest EARTH_HEART / FOUNDATION
    elif [ "$SHADOW" -gt 40 ]; then
        HINT="LIMIT_ASCENT"        # avoid highest modes for a while
    else
        case "$DIR" in
            ASCEND_POWER)   HINT="ALLOW_ASCENT" ;;
            STABILIZE_GROUND) HINT="PREFER_STABLE" ;;
            CONTAIN_DRIFT)  HINT="REDUCE_DRIFT" ;;
            CHANNEL_FIRE)   HINT="ALLOW_BURNING" ;;
            *)              HINT="HOLD_STATE" ;;
        esac
    fi

    memory_set "vairaj_hint" "$HINT"
    echo "🜇 Vairaj Behavior Hint → $HINT (DIR=$DIR | SHADOW=$SHADOW)" >> "$VAIRAJ_LOG"
}

# ----------------------------------------------------------
#  VAIRAJ TRUST METER
#  How “aligned” the system feels with itself over time
# ----------------------------------------------------------
vairaj_update_trust() {
    TR=$(memory_get "vairaj_trust")
    SHADOW=$(memory_get "vairaj_shadow_level")
    STAB=$(memory_get "power_stability")

    # Trust rises with stability, falls with shadow
    TR=$((TR + STAB / 20 - SHADOW / 20))

    [ "$TR" -lt 0 ] && TR=0
    [ "$TR" -gt 100 ] && TR=100

    memory_set "vairaj_trust" "$TR"
    echo "🤝 Vairaj Trust → $TR" >> "$VAIRAJ_LOG"
}

# ----------------------------------------------------------
#  PUBLIC ENTRYPOINT
#  Call this from your mega kernel once per cycle
# ----------------------------------------------------------
vairaj_cycle() {
    echo "--- VAIRAJ CYCLE START ---" >> "$VAIRAJ_LOG"
    vairaj_pick_directive
    vairaj_shadow_scan
    vairaj_behavior_hint
    vairaj_update_trust
    echo "--- VAIRAJ CYCLE END ---" >> "$VAIRAJ_LOG"
    echo "" >> "$VAIRAJ_LOG"
}

# If this file is executed directly, run one Vairaj cycle
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    vairaj_cycle
fi
