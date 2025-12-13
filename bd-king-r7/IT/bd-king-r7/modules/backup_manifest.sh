#!/usr/bin/env bash
# Backup Manifest
while :; do
  tar -cf "$HOME/bd_king_r7/archive/state_$(date +%Y%m%d_%H%M%S).tar" "$HOME/bd_king_r7/config" "$HOME/bd_king_r7/run" "$HOME/bd_king_r7/logs" 2>/dev/null
  echo "$(date +"%F %T") [BACKUP] Snapshot sealed." >> "$HOME/bd_king_r7/run/BACKUP.hb"
  sleep 60
done
