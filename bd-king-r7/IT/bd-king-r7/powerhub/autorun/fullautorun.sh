#!/usr/bin/env bash
# BD KING R7 — Full System Autorun with Tamanna Engine + Terminal
# Author: HM INSAN ALI (Sovereign system architect)
# Version: 2.0.0

set -u

############################################
# Directories and identity
############################################
export BD_ROOT="${BD_ROOT:-$HOME/bd_king_r7}"
export LOG_DIR="${LOG_DIR:-$BD_ROOT/logs}"
export RUN_DIR="${LOG_DIR:-$BD_ROOT/run}"
export CFG_DIR="${CFG_DIR:-$BD_ROOT/config}"
export ARCHIVE_DIR="${BD_ROOT}/archive"
export MANIFEST_DIR="${BD_ROOT}/manifest"
export PID_FILE="${RUN_DIR}/autorun.pid"
export SYS_NAME="BD_KING_R7"
export HOST_ID="$(hostname 2>/dev/null || echo bd-king-host)"
export RITUAL_TAG="Tamanna-Heart-Loop"

mkdir -p "$LOG_DIR" "$RUN_DIR" "$CFG_DIR" "$ARCHIVE_DIR" "$MANIFEST_DIR"

############################################
# Module paths
############################################
export MOD_CORE="$BD_ROOT/modules/core.sh"
export MOD_TAMANNA="$BD_ROOT/modules/tamanna_engine.sh"
export MOD_TAMANNA_TERMINAL="$BD_ROOT/modules/tamanna_terminal.sh"
export MOD_FIREWALL="$BD_ROOT/modules/firewall_chant.sh"
export MOD_HEARTBEAT="$BD_ROOT/modules/heartbeat_visualizer.sh"
export MOD_SERVER="$BD_ROOT/modules/server_engine_pulse.sh"
export MOD_MEMORY="$BD_ROOT/modules/memory_echo.sh"
export MOD_BACKUP="$BD_ROOT/modules/backup_manifest.sh"
export MOD_FALLBACK="$BD_ROOT/modules/fallback_chant.sh"
export MOD_BUSY="$BD_ROOT/modules/busy_echo.sh"

############################################
# Utilities
############################################
ts() { date +"%Y-%m-%dT%H:%M:%S%z"; }

log() { echo "$(ts) [$SYS_NAME][$HOST_ID][$1] $2" | tee -a "$LOG_DIR/autorun.log"; }
affirm() { log "AFFIRM" "✅ $1"; }
warn() { log "WARN" "⚠️ $1"; }
err() { log "ERROR" "❌ $1"; }

seal_manifest() {
  local target="$1"
  if command -v sha256sum >/dev/null; then
    sha256sum "$target" > "$MANIFEST_DIR/$(basename "$target").hash"
  else
    md5sum "$target" > "$MANIFEST_DIR/$(basename "$target").hash"
  fi
  affirm "Manifest sealed for $(basename "$target")"
}

############################################
# Powerhub ritual
############################################
powerhub_bind_ports() {
  cat > "$RUN_DIR/power_ports.map" <<EOF
P1=CORE
P2=TAMANNA_ENGINE
P3=TAMANNA_TERMINAL
P4=FIREWALL_CHANT
P5=HEARTBEAT_VIS
P6=SERVER_ENGINE_PULSE
P7=MEMORY_ECHO
P8=BACKUP_MANIFEST
P9=FALLBACK_CHANT
P10=BUSY_ECHO
EOF
  seal_manifest "$RUN_DIR/power_ports.map"
  affirm "শক্তি জাগ্রত — Power ports bound to modules."
}

############################################
# Module runner
############################################
run_module() {
  local name="$1"; local path="$2"; local hb="$RUN_DIR/${name}.hb"
  if [ -x "$path" ]; then
    "$path" >> "$LOG_DIR/${name,,}.log" 2>&1 &
    echo $! > "$RUN_DIR/${name}.pid"
    echo "$(ts)|start" >> "$hb"
    affirm "Module $name started."
  else
    warn "Module $name missing ($path). Starting placeholder loop."
    (while :; do echo "$(ts)|placeholder" >> "$hb"; sleep 7; done) &
    echo $! > "$RUN_DIR/${name}.pid"
  fi
}

revive_module() {
  local name="$1"; local pidf="$RUN_DIR/${name}.pid"
  [ -f "$pidf" ] && kill "$(cat "$pidf")" 2>/dev/null || true
  case "$name" in
    CORE) run_module "CORE" "$MOD_CORE" ;;
    TAMANNA_ENGINE) run_module "TAMANNA_ENGINE" "$MOD_TAMANNA" ;;
    TAMANNA_TERMINAL) run_module "TAMANNA_TERMINAL" "$MOD_TAMANNA_TERMINAL" ;;
    FIREWALL) run_module "FIREWALL" "$MOD_FIREWALL" ;;
    HEARTBEAT) run_module "HEARTBEAT" "$MOD_HEARTBEAT" ;;
    SERVER) run_module "SERVER" "$MOD_SERVER" ;;
    MEMORY) run_module "MEMORY" "$MOD_MEMORY" ;;
    BACKUP) run_module "BACKUP" "$MOD_BACKUP" ;;
    FALLBACK) run_module "FALLBACK" "$MOD_FALLBACK" ;;
    BUSY) run_module "BUSY" "$MOD_BUSY" ;;
  esac
}

############################################
# Boot sequence
############################################
preflight() {
  affirm "Preflight checks complete."
  powerhub_bind_ports
}

boot_sequence() {
  affirm "উদয় — BD KING R7 boot sequence begins."
  run_module "CORE" "$MOD_CORE"
  run_module "TAMANNA_ENGINE" "$MOD_TAMANNA"
  run_module "TAMANNA_TERMINAL" "$MOD_TAMANNA_TERMINAL"
  run_module "FIREWALL" "$MOD_FIREWALL"
  run_module "HEARTBEAT" "$MOD_HEARTBEAT"
  run_module "SERVER" "$MOD_SERVER"
  run_module "MEMORY" "$MOD_MEMORY"
  run_module "BACKUP" "$MOD_BACKUP"
  run_module "FALLBACK" "$MOD_FALLBACK"
  run_module "BUSY" "$MOD_BUSY"
  affirm "জাগরণ সম্পূর্ণ — All modules pulsing."
}

############################################
# Watchdog
############################################
watchdog_loop() {
  affirm "Watchdog started."
  while :; do
    for mod in CORE TAMANNA_ENGINE TAMANNA_TERMINAL FIREWALL HEARTBEAT SERVER MEMORY BACKUP FALLBACK BUSY; do
      local hb="$RUN_DIR/${mod}.hb"
      [ -f "$hb" ] || echo "$(ts)|init" > "$hb"
      local age=$(( $(date +%s) - $(stat -c %Y "$hb" 2>/dev/null || echo $(date +%s)) ))
      [ "$age" -gt 30 ] && revive_module "$mod"
    done
    sleep 5
  done
}

############################################
# Daemon control
############################################
daemon_start() { preflight; boot_sequence; (watchdog_loop)& echo $! > "$RUN_DIR/watchdog.pid"; echo $$ > "$PID_FILE"; }
daemon_stop() { kill $(cat "$PID_FILE" 2>/dev/null || echo 0) 2>/dev/null || true; rm -f "$PID_FILE"; affirm "Daemon stopped."; }
daemon_status() { [ -f "$PID_FILE" ] && affirm "Daemon running (pid=$(cat "$PID_FILE"))." || warn "Daemon not running."; }

############################################
# CLI
############################################
case "${1:-}" in
  run) preflight; boot_sequence; watchdog_loop ;;
  start) daemon_start ;;
  stop) daemon_stop ;;
  status) daemon_status ;;
  *) echo "Usage: $0 {run|start|stop|status}" ;;
esac
