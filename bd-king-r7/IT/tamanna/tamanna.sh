#!/usr/bin/env bash
# file: code_watcher.sh
WATCH_DIR="/srv/bd_king_r7/tamanna"
LOG="./code_watcher.log"

inotifywait -m -r -e close_write,modify,create,delete "$WATCH_DIR" --format '%w%f' |
while read FILE; do
  echo "$(date '+%F %T') CHANGED $FILE" | tee -a "$LOG"
  # run formatter and linter
  python -m black "$WATCH_DIR" || true
  python -m flake8 "$WATCH_DIR" || true
  # commit and push
  cd "$WATCH_DIR"
  git add -A
  git commit -m "auto: change $(date '+%F %T')" || true
  git push origin main || true
  # optional: call master utility to sync or deploy
  /usr/bin/python3 /srv/bd_king_r7/tamanna_master.py sync
done
