#!/bin/bash
# board1670-heartbeat.sh
LOG="/var/log/board1670_autofix.log"
SERVICE="board1670.service"

timestamp() { date +"%F %T"; }

# Heartbeat: confirm service health
if ! systemctl is-active --quiet "$SERVICE"; then
  echo "$(timestamp) Service down — attempting restart" | tee -a "$LOG"
  systemctl restart "$SERVICE"
  sleep 5
  systemctl is-active --quiet "$SERVICE" && \
    echo "$(timestamp) Revival confirmed" >> "$LOG" || \
    echo "$(timestamp) Revival failed — escalate" >> "$LOG"
fi

# Config integrity: detect drift
CFG="/etc/board1670/product.conf"
EXPECTED_ID="0692120000204610000610100"

if ! grep -q "$EXPECTED_ID" "$CFG"; then
  echo "$(timestamp) Config ID drift detected — restoring manifest" >> "$LOG"
  cp /usr/share/board1670/manifests/product.conf "$CFG"
fi
