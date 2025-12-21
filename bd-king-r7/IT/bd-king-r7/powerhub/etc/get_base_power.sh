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
        # NEW Ω-TIER:
        VAIRAJ_SIGMA) echo 285000 ;;
        VAIRAJ_OMEGA) echo 320000 ;;
        VAIRAJ_AURORA) echo 360000 ;;
        VAIRAJ_INFINITY) echo 400000 ;;
        *) echo 1523 ;;
    esac
}
power_fusion() {
    MODE=$(memory_get "power_mode")
    BASE=$(get_base_power "$MODE")
    DRIFT=$(memory_get "power_drift")
    STAB=$(memory_get "power_stability")
    FF=$(memory_get "force_field")

    FUSION=$((100 + DRIFT - (100 - STAB) / 2 + (RANDOM % 15 - 7)))

    case "$FF" in
        DOMINION)   FUSION=$((FUSION + 5)) ;;
        IGNITION)   FUSION=$((FUSION + 15)) ;;
        FOUNDATION) FUSION=$((FUSION - 10)) ;;
        RESONANCE)  FUSION=$((FUSION + 0)) ;;
        NULL)       FUSION=100 ;;
    esac

    [ "$FUSION" -lt 50 ] && FUSION=50
    [ "$FUSION" -gt 200 ] && FUSION=200

    # 🔥 Overdrive layer
    OD=$(get_overdrive_multiplier)
    FUSION=$((FUSION * OD / 100))

    POWER=$((BASE * FUSION / 100))

    echo "⚡ MODE: $MODE | FF: $FF | Base: $BASE W | Fusion: ${FUSION}% → $POWER W" >> "$LOG"
}
get_overdrive_multiplier() {
    MODE=$(memory_get "power_mode")
    case "$MODE" in
        VAIRAJ_SIGMA)    echo 115 ;;  # +15%
        VAIRAJ_OMEGA)    echo 130 ;;  # +30%
        VAIRAJ_AURORA)   echo 150 ;;  # +50%
        VAIRAJ_INFINITY) echo 180 ;;  # +80%
        *)               echo 100 ;;  # normal
    esac
}
