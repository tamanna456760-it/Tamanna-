#!/usr/bin/env bash
# Tamanna Terminal — interactive shell
LOG="$HOME/bd_king_r7/logs/tamanna_terminal.log"
HB="$HOME/bd_king_r7/run/TAMANNA_TERMINAL.hb"

echo "Tamanna Terminal ready. Commands: affirm, heartbeat, memory, fallback, exit."
while true; do
  read -rp "tamanna> " cmd args
  case "$cmd" in
    affirm)   echo "$(date +"%F %T") [AFFIRM] $args" | tee -a "$LOG" ;;
    heartbeat) echo "$(date +"%F %T") [HB] bpm=${args:-72}" >> "$HB" ;;
    memory)   echo "$(date +"%F %T") [MEMORY] $args" >> "$HOME/bd_king_r7/run/tamanna.memory" ;;
    fallback) echo "$(date +"%F %T") [FALLBACK] $args" >> "$LOG" ;;
    exit)     echo "Closing Tamanna Terminal."; break ;;
    *)        echo "Unknown command: $cmd" ;;
  esac
done
