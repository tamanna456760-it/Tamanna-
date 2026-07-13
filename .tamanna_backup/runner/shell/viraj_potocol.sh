# After: bash "$ROOT/bd_king_r7_vairaj_engine.sh"

VAIRAJ_HINT=$(grep "^vairaj_hint=" "$STATE" 2>/dev/null | cut -d '=' -f2)

MODE=$(memory_get "power_mode")
FF=$(memory_get "force_field")
STAB=$(memory_get "power_stability")
DRIFT=$(memory_get "power_drift")

case "$VAIRAJ_HINT" in
    FORCE_GROUND)
        MODE="EARTH_HEART"
        FF="FOUNDATION"
        ;;
    LIMIT_ASCENT)
        case "$MODE" in
            VOID_CROWN|QUANTUM_VOID|INFERNO_DRIVE)
                MODE="CELESTIAL_CORE"
                ;;
        esac
        ;;
    ALLOW_ASCENT)
        if [ "$STAB" -gt 60 ]; then
            # allow high modes, maybe boost one step
            [ "$MODE" = "OMEGA_ASCEND" ] && MODE="VOID_CROWN"
        fi
        ;;
    REDUCE_DRIFT)
        DRIFT=$((DRIFT / 2))
        ;;
    PREFER_STABLE)
        case "$MODE" in
            VOID_CROWN|QUANTUM_VOID|INFERNO_DRIVE|TEMPEST_ASCENT)
                MODE="EARTH_HEART"
                ;;
        esac
        ;;
    *)
        # HOLD_STATE or unknown → do nothing
        ;;
esac

memory_set "power_mode" "$MODE"
memory_set "force_field" "$FF"
memory_set "power_drift" "$DRIFT"

echo "📡 Vairaj Protocol Applied — HINT=$VAIRAJ_HINT | MODE=$MODE | FIELD=$FF | DRIFT=$DRIFT" >> "$LOG"
# Vairaj Emergency Power Unlock
VAIRAJ_HINT=$(memory_get "vairaj_hint")
VAIRAJ_TRUST=$(memory_get "vairaj_trust")
SHADOW=$(memory_get "vairaj_shadow_level")
STAB=$(memory_get "power_stability")
MODE=$(memory_get "power_mode")

# Condition for Ω-tier unlock:
# - high trust
# - low shadow
# - good stability
if [ "$VAIRAJ_TRUST" -gt 70 ] && [ "$SHADOW" -lt 25 ] && [ "$STAB" -gt 65 ]; then
    case "$VAIRAJ_HINT" in
        ALLOW_ASCENT|ALLOW_BURNING)
            case "$MODE" in
                OMEGA_ASCEND|VOID_CROWN|QUANTUM_VOID|INFERNO_DRIVE)
                    MODE="VAIRAJ_SIGMA"
                    ;;
                VAIRAJ_SIGMA)
                    MODE="VAIRAJ_OMEGA"
                    ;;
                VAIRAJ_OMEGA)
                    MODE="VAIRAJ_AURORA"
                    ;;
                VAIRAJ_AURORA)
                    MODE="VAIRAJ_INFINITY"
                    ;;
            esac
            echo "🚨 Vairaj Emergency Power Unlock → $MODE" >> "$LOG"
            ;;
    esac
fi

memory_set "power_mode" "$MODE"
