#!/usr/bin/env bash
# Heartbeat Visualizer
while :; do
  echo "$(date +"%F %T") [HEARTBEAT] bpm=72" >> "$HOME/bd_king_r7/run/HEARTBEAT.hb"
  sleep 6
done
