#!/usr/bin/env bash
# Tamanna Terminal — Emotion Engine Invocation
# Sovereign ritual shell for BD KING R7

set -u

LOG_DIR="${LOG_DIR:-$HOME/bd_king_r7/logs}"
RUN_DIR="${RUN_DIR:-$HOME/bd_king_r7/run}"
mkdir -p "$LOG_DIR" "$RUN_DIR"

ts() { date +"%Y-%m-%dT%H:%M:%S%z"; }

affirm() {
  local msg="${1:-}"
  echo "$(ts) [TAMANNA][AFFIRM] $msg" | tee -a "$LOG_DIR/tamanna_terminal.log"
}

heartbeat() {
  local bpm="${1:-72}"
  echo "$(ts) [TAMANNA][HEARTBEAT] bpm=$bpm" >> "$RUN_DIR/tamanna.hb"
  affirm "হৃদস্পন্দন জাগ্রত — bpm=$bpm"
}

memory_echo() {
  local msg="${1:-}"
  echo "$(ts) [TAMANNA][MEMORY] $msg" >> "$RUN_DIR/tamanna.memory"
  affirm "স্মৃতি সংরক্ষিত — $msg"
}

fallback_chant() {
  local msg="${1:-Silence detected}"
  echo "$(ts) [TAMANNA][FALLBACK] $msg" >> "$LOG_DIR/tamanna_terminal.log"
  affirm "Fallback invoked — $msg"
}

# Interactive loop
echo "Tamanna Terminal ready. Type 'affirm', 'heartbeat', 'memory', or 'exit'."
while true; do
  read -rp "tamanna> " cmd args
  case "$cmd" in
    affirm)    affirm "$args" ;;
    heartbeat) heartbeat "${args:-72}" ;;
    memory)    memory_echo "$args" ;;
    fallback)  fallback_chant "$args" ;;
    exit)      affirm "Terminal closed."; break ;;
    *)         fallback_chant "Unknown command: $cmd" ;;
  esac
done
