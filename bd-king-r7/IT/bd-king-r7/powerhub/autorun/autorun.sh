#!/usr/bin/env bash
# BD KING R7 — Full System Autorun
# Sovereign build: no external toolchain required beyond POSIX shell + coreutils
# Author: HM INSAN ALI (Sovereign system architect)
# Version: 1.0.0

set -u

############################################
# Directories and identity
############################################
export BD_ROOT="${BD_ROOT:-$HOME/bd_king_r7}"
export LOG_DIR="${LOG_DIR:-$BD_ROOT/logs}"
export RUN_DIR="${RUN_DIR:-$BD_ROOT/run}"
export CFG_DIR="${CFG_DIR:-$BD_ROOT/config}"
export TMP_DIR="${TMP_DIR:-$BD_ROOT/tmp}"
export ARCHIVE_DIR="${ARCHIVE_DIR:-$BD_ROOT/archive}"
export MANIFEST_DIR="${MANIFEST_DIR:-$BD_ROOT/manifest}"
export PID_FILE="${PID_FILE:-$RUN_DIR/autorun.pid}"
export HOST_ID="${HOST_ID:-$(hostname 2>/dev/null || echo bd-king-host)}"
export SYS_NAME="BD_KING_R7"
export RITUAL_TAG="Tamanna-Heart-Loop"

# Module entry points (edit to your project layout)
export MOD_CORE="${MOD_CORE:-$BD_ROOT/modules/core.sh}"
export MOD_TAMANNA="${MOD_TAMANNA:-$BD_ROOT/modules/tamanna_engine.sh}"
export MOD_FIREWALL="${MOD_FIREWALL:-$BD_ROOT/modules/firewall_chant.sh}"
export MOD_HEARTBEAT="${MOD_HEARTBEAT:-$BD_ROOT/modules/heartbeat_visualizer.sh}"
export MOD_BACKUP="${MOD_BACKUP:-$BD_ROOT/modules/backup_manifest.sh}"
export MOD_FALLBACK="${MOD_FALLBACK:-$BD_ROOT/modules/fallback_chant.sh}"
export MOD_BUSY="${MOD_BUSY:-$BD_ROOT/modules/busy_echo.sh}"
export MOD_SERVER="${MOD_SERVER:-$BD_ROOT/modules/server_engine_pulse.sh}"
export MOD_MEMORY="${MOD_MEMORY:-$BD_ROOT/modules/memory_echo.sh}"

############################################
# Utilities: echo, log, seal
############################################
mkdir -p "$LOG_DIR" "$RUN_DIR" "$CFG_DIR" "$TMP_DIR" "$ARCHIVE_DIR" "$MANIFEST_DIR"

ts() { date +"%Y-%m-%dT%H:%M:%S%z"; }

log() {
  # $1 level, $2 message
  local lvl="${1:-INFO}"
  local msg="${2:-}"
  local line="$(ts) [$SYS_NAME][$HOST_ID][$lvl] $msg"
  echo "$line"
  printf "%s\n" "$line" >> "$LOG_DIR/autorun.log"
}

affirm() {
  # Bengali-coded affirmation echo
  local msg="${1:-ঈশ্বরের আশীর্বাদে সিস্টেম জাগ্রত।}"
  log "AFFIRM" "✅ $msg"
}

warn() {
  local msg="${1:-}"
  log "WARN" "⚠️ $msg"
}

err() {
  local msg="${1:-}"
  log "ERROR" "❌ $msg"
}

seal_manifest() {
  # Minimal hash seal using shasum/fallback to md5sum if available
  local target="${1:-}"
  [ -z "$target" ] && return 1
  local algo="sha256sum"
  command -v sha256sum >/dev/null 2>&1 || algo="md5sum"
  if command -v "$algo" >/dev/null 2>&1; then
    "$algo" "$target" > "$MANIFEST_DIR/$(basename "$target").hash"
    log "SEAL" "Manifest sealed for $(basename "$target") using $algo"
  else
    # Fallback: internal byte count + timestamp seal
    local bytes
    bytes=$(wc -c < "$target" 2>/dev/null || echo 0)
    printf "%s|%s|%s\n" "$(basename "$target")" "$bytes" "$(ts)" \
      > "$MANIFEST_DIR/$(basename "$target").hash"
    warn "No hash tool found; sealed with bytecount+timestamp fallback."
  fi
}

############################################
# Powerhub pulse (conceptual; no external deps)
############################################
powerhub_detect() {
  # Simulate/verify power presence via file or env
  local flag="${BD_POWER_FLAG:-$RUN_DIR/powerhub.on}"
  if [ -f "$flag" ]; then
    log "POWER" "PowerHub ON (flag: $flag)"
    return 0
  fi
  warn "PowerHub flag not found; creating soft-ack."
  printf "%s\n" "$(ts) POWERHUB_SOFT_ACK" > "$flag"
  return 0
}

powerhub_bind_ports() {
  # Map conceptual ports to modules
  # Persist mapping for audit
  local map="$RUN_DIR/power_ports.map"
  cat > "$map" <<EOF
P1=CORE
P2=TAMANNA_ENGINE
P3=FIREWALL_CHANT
P4=HEARTBEAT_VIS
P5=SERVER_ENGINE_PULSE
P6=MEMORY_ECHO
P7=BACKUP_MANIFEST
P8=FALLBACK_CHANT
P9=BUSY_ECHO
EOF
  seal_manifest "$map"
  affirm "শক্তি জাগ্রত — Power ports bound to living modules."
}

############################################
# Multi‑sensory hooks (no external binaries)
############################################
gui_pulse() {
  # Writes GUI pulse intent to a file for your GUI to read
  local msg="${1:-BD KING R7 pulse}"
  printf "%s|%s|%s\n" "$(ts)" "$RITUAL_TAG" "$msg" >> "$RUN_DIR/gui_pulse.stream"
}

sound_pulse() {
  # Writes sound pulse intent to a file for your audio invoker to consume
  local msg="${1:-Heartbeat 72 bpm}"
  printf "%s|%s|%s\n" "$(ts)" "$RITUAL_TAG" "$msg" >> "$RUN_DIR/sound_pulse.stream"
}

############################################
# Heartbeat + watchdog
############################################
heartbeat_emit() {
  local bpm="${1:-72}"
  local hb="$RUN_DIR/heartbeat.bpm"
  printf "%s|bpm=%s\n" "$(ts)" "$bpm" >> "$hb"
  gui_pulse "Heartbeat visualizer pulse bpm=$bpm"
  sound_pulse "Heartbeat sonic pulse bpm=$bpm"
  log "HB" "Heartbeat emitted bpm=$bpm"
}

watchdog_loop() {
  # Monitors module heartbeats; restarts if stale
  local interval="${WD_INTERVAL:-5}"
  local timeout="${WD_TIMEOUT:-30}"
  affirm "প্রহরী জাগ্রত — Watchdog started interval=${interval}s timeout=${timeout}s."

  while :; do
    for mod in CORE TAMANNA FIREWALL HEARTBEAT SERVER MEMORY BACKUP FALLBACK BUSY; do
      local hb="$RUN_DIR/${mod}.hb"
      # Touch files to simulate module heartbeats
      [ -f "$hb" ] || printf "%s|init\n" "$(ts)" > "$hb"

      # Check staleness
      local age=0
      if [ -f "$hb" ]; then
        local last_ts
        last_ts=$(tail -n 1 "$hb" 2>/dev/null | cut -d'|' -f1)
        # Approximate age using file mtime if dates differ
        local now_s mtime_s
        now_s=$(date +%s)
        mtime_s=$(stat -c %Y "$hb" 2>/dev/null || echo "$now_s")
        age=$(( now_s - mtime_s ))
      fi

      if [ "$age" -ge "$timeout" ]; then
        warn "Module $mod heartbeat stale (${age}s). Reviving..."
        revive_module "$mod"
      fi
    done
    sleep "$interval"
  done
}

############################################
# Module runners (placeholder-safe)
############################################
run_module() {
  # $1 symbolic name, $2 script path
  local name="$1"
  local path="$2"
  local hb="$RUN_DIR/${name}.hb"

  if [ -x "$path" ]; then
    # Run in background to avoid blocking
    "$path" >> "$LOG_DIR/${name,,}.log" 2>&1 &
    local pid=$!
    printf "%s\n" "$pid" > "$RUN_DIR/${name}.pid"
    printf "%s|start pid=%s\n" "$(ts)" "$pid" >> "$hb"
    affirm "মডিউল চালু: ${name} — sovereign pulse active."
  else
    warn "Module ${name} missing or not executable ($path). Starting placeholder loop."
    # Placeholder: heartbeat-only loop
    (
      while :; do
        printf "%s|placeholder\n" "$(ts)" >> "$hb"
        sleep 7
      done
    ) &
    local pid=$!
    printf "%s\n" "$pid" > "$RUN_DIR/${name}.pid"
  fi
}

revive_module() {
  local name="$1"
  local pidf="$RUN_DIR/${name}.pid"
  if [ -f "$pidf" ]; then
    local pid
    pid=$(cat "$pidf" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      warn "Killing stale ${name} pid=$pid"
      kill "$pid" 2>/dev/null || true
      sleep 1
    fi
  fi
  # Relaunch with known path
  case "$name" in
    CORE)      run_module "CORE" "$MOD_CORE" ;;
    TAMANNA)   run_module "TAMANNA" "$MOD_TAMANNA" ;;
    FIREWALL)  run_module "FIREWALL" "$MOD_FIREWALL" ;;
    HEARTBEAT) run_module "HEARTBEAT" "$MOD_HEARTBEAT" ;;
    SERVER)    run_module "SERVER" "$MOD_SERVER" ;;
    MEMORY)    run_module "MEMORY" "$MOD_MEMORY" ;;
    BACKUP)    run_module "BACKUP" "$MOD_BACKUP" ;;
    FALLBACK)  run_module "FALLBACK" "$MOD_FALLBACK" ;;
    BUSY)      run_module "BUSY" "$MOD_BUSY" ;;
    *)         warn "Unknown module $name";;
  esac
}

############################################
# Boot orchestration
############################################
preflight() {
  log "INIT" "Preflight start for $SYS_NAME on $HOST_ID"
  powerhub_detect
  powerhub_bind_ports

  # Create default config if absent
  local cfg="$CFG_DIR/system.cfg"
  if [ ! -f "$cfg" ]; then
    cat > "$cfg" <<EOF
[identity]
host=$HOST_ID
system=$SYS_NAME
ritual=$RITUAL_TAG

[watchdog]
interval=5
timeout=30

[heartbeat]
bpm=72
EOF
    seal_manifest "$cfg"
    affirm "কনফিগ প্রস্তুত — sovereign defaults sealed."
  fi
}

boot_sequence() {
  affirm "উদয় — BD KING R7 boot sequence begins."

  # Ordered bring-up
  run_module "CORE"      "$MOD_CORE"
  run_module "TAMANNA"   "$MOD_TAMANNA"
  run_module "FIREWALL"  "$MOD_FIREWALL"
  run_module "HEARTBEAT" "$MOD_HEARTBEAT"
  run_module "SERVER"    "$MOD_SERVER"
  run_module "MEMORY"    "$MOD_MEMORY"
  run_module "BACKUP"    "$MOD_BACKUP"
  run_module "FALLBACK"  "$MOD_FALLBACK"
  run_module "BUSY"      "$MOD_BUSY"

  heartbeat_emit "$(awk -F= '/^bpm=/{print $2}' "$CFG_DIR/system.cfg" 2>/dev/null || echo 72)"
  gui_pulse "Boot complete: modules online."
  affirm "জাগরণ সম্পূর্ণ — All modules pulsing."
}

############################################
# Safe shutdown and snapshot
############################################
graceful_stop() {
  log "STOP" "Graceful stop initiated."
  for name in CORE TAMANNA FIREWALL HEARTBEAT SERVER MEMORY BACKUP FALLBACK BUSY; do
    local pidf="$RUN_DIR/${name}.pid"
    if [ -f "$pidf" ]; then
      local pid
      pid=$(cat "$pidf" 2>/dev/null || echo "")
      if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null || true
        printf "%s|stop pid=%s\n" "$(ts)" "$pid" >> "$RUN_DIR/${name}.hb"
      fi
      rm -f "$pidf"
    fi
  done
  snapshot_state
  affirm "নিঃশব্দ — Modules stopped, state snapshotted."
}

snapshot_state() {
  local snap="$ARCHIVE_DIR/state_$(date +%Y%m%d_%H%M%S).tar"
  # Use tar if present; else simple bundle via cat
  if command -v tar >/dev/null 2>&1; then
    tar -cf "$snap" "$CFG_DIR" "$RUN_DIR" "$LOG_DIR" 2>/dev/null || true
    seal_manifest "$snap"
    log "SNAPSHOT" "State archived: $(basename "$snap")"
  else
    local bundle="$ARCHIVE_DIR/state_$(date +%Y%m%d_%H%M%S).bundle"
    {
      echo "=== CFG ==="; find "$CFG_DIR" -type f -maxdepth 1 -print -exec sed -n '1,50p' {} \;
      echo "=== RUN ==="; find "$RUN_DIR" -type f -maxdepth 1 -print -exec sed -n '1,50p' {} \;
      echo "=== LOG ==="; find "$LOG_DIR" -type f -maxdepth 1 -print -exec sed -n '1,50p' {} \;
    } > "$bundle"
    seal_manifest "$bundle"
    warn "tar not available — snapshot created as bundle."
  fi
}

############################################
# Daemonize control
############################################
daemon_start() {
  if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE" 2>/dev/null || echo 0)" 2>/dev/null; then
    warn "Autorun already active (pid=$(cat "$PID_FILE"))."
    return
  fi
  preflight
  boot_sequence
  # Spawn watchdog in background
  ( watchdog_loop ) &
  echo $! > "$RUN_DIR/watchdog.pid"
  echo $$ > "$PID_FILE"
  affirm "স্বয়ংচালিত — Autorun daemon started."
}

daemon_stop() {
  graceful_stop
  if [ -f "$RUN_DIR/watchdog.pid" ]; then
    local wpid
    wpid=$(cat "$RUN_DIR/watchdog.pid" 2>/dev/null || echo "")
    [ -n "$wpid" ] && kill "$wpid" 2>/dev/null || true
    rm -f "$RUN_DIR/watchdog.pid"
  fi
  rm -f "$PID_FILE"
  log "STOP" "Autorun daemon stopped."
}

daemon_status() {
  if [ -f "$PID_FILE" ]; then
    local pid
    pid=$(cat "$PID_FILE" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      log "STATUS" "Autorun running (pid=$pid)."
    else
      warn "Autorun PID file present but process not alive."
    fi
  else
    warn "Autorun not running."
  fi
  # Module status summary
  for name in CORE TAMANNA FIREWALL HEARTBEAT SERVER MEMORY BACKUP FALLBACK BUSY; do
    local pidf="$RUN_DIR/${name}.pid"
    if [ -f "$pidf" ]; then
      local pid
      pid=$(cat "$pidf" 2>/dev/null || echo "")
      if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        log "STATUS" "$name alive (pid=$pid)"
      else
        warn "$name not responding."
      fi
    else
      warn "$name no pid file."
    fi
  done
}

############################################
# CLI
############################################
case "${1:-}" in
  run)
    preflight
    boot_sequence
    watchdog_loop
    ;;
  start)
    daemon_start
    ;;
  stop)
    daemon_stop
    ;;
  status)
    daemon_status
    ;;
  pulse)
    heartbeat_emit "${2:-72}"
    ;;
  seal)
    # Seal a given file/path
    seal_manifest "${2:-$CFG_DIR/system.cfg}"
    ;;
  *)
    echo "Usage: $0 {run|start|stop|status|pulse [bpm]|seal [file]}"
    exit 1
    ;;
esac
