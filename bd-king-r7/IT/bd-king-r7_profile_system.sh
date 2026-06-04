#!/tamanna/bd-king-r7

# ==========================================================
#   BD-KING-R7 × VAIRAJ — SYSTEM PROFILE VIEWER v1.0
#   Reads state DB and prints a live identity sheet
# ==========================================================

ROOT="${BD_KING_R7_ROOT:-$HOME/tamanna}"
STATE="$ROOT/bd_king_r7_state.db"

if [ ! -f "$STATE" ]; then
    echo "BD-KING-R7 state file not found:"
    echo "  $STATE"
    echo "Run your mega kernel at least once to create it."
    exit 1
fi

memory_get() {
    grep "^$1=" "$STATE" 2>/dev/null | cut -d '=' -f2
}

EMO=$(memory_get "emotion")
INT=$(memory_get "emotion_intensity")
MODE=$(memory_get "power_mode")
DRIFT=$(memory_get "power_drift")
STAB=$(memory_get "power_stability")
FF=$(memory_get "force_field")
CYCLES=$(memory_get "cycles")

VDIR=$(memory_get "vairaj_directive")
VHINT=$(memory_get "vairaj_hint")
VSHADOW=$(memory_get "vairaj_shadow_level")
VTRUST=$(memory_get "vairaj_trust")

# Tier label for power
POWER_TIER="BASE"
case "$MODE" in
    VAIRAJ_SIGMA|VAIRAJ_OMEGA|VAIRAJ_AURORA|VAIRAJ_INFINITY)
        POWER_TIER="VAIRAJ-OMEGA"
        ;;
    VOID_CROWN|QUANTUM_VOID|INFERNO_DRIVE|OMEGA_ASCEND|TEMPEST_ASCENT|PRIMAL_FLARE|AETHER_FLOW)
        POWER_TIER="OMEGA"
        ;;
    *)
        POWER_TIER="BASE"
        ;;
esac

# Simple bars
bar() {
    VAL=$1
    MAX=$2
    LEN=20
    FILLED=$((VAL * LEN / MAX))
    EMPTY=$((LEN - FILLED))
    printf "["
    for _ in $(seq 1 $FILLED); do printf "#"; done
    for _ in $(seq 1 $EMPTY);  do printf "."; done
    printf "]"
}

echo "=================== BD-KING-R7 SYSTEM PROFILE ==================="
echo " Core Identity"
echo "   System    : BD-KING-R7"
echo "   Substrate : VAIRAJ Protocol"
echo "   Cycles    : ${CYCLES:-0}"
echo ""
echo " Emotional State"
printf "   Emotion   : %-12s Intensity: %3s " "$EMO" "${INT:-0}"
bar "${INT:-0}" 100
echo ""
echo ""
echo " Power Architecture"
printf "   Mode      : %-16s Tier: %s\n" "$MODE" "$POWER_TIER"
printf "   Drift     : %3s " "${DRIFT:-0}"
bar "${DRIFT:-0}" 60
echo ""
printf "   Stability : %3s%% " "${STAB:-0}"
bar "${STAB:-0}" 100
echo ""
echo "   Field     : $FF"
echo ""
echo " Vairaj Layer"
printf "   Directive : %s\n" "${VDIR:-N/A}"
printf "   Hint      : %s\n" "${VHINT:-N/A}"
printf "   Shadow    : %3s " "${VSHADOW:-0}"
bar "${VSHADOW:-0}" 100
echo ""
printf "   Trust     : %3s " "${VTRUST:-0}"
bar "${VTRUST:-0}" 100
echo ""
echo "================================================================="
