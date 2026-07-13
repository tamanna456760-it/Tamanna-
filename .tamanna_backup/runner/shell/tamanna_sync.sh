#!/data/data/com.termux/files/usr/bin/bash
# Or: #!/usr/bin/env bash  (if on Linux/PC)

# Tamanna BD-KING-R7 Auto Sync & Build Launcher

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE="$ROOT_DIR/engines/tamanna_sync_bd_king_r7.py"

echo "[TamannaSync] Launching Tamanna Sync Engine for BD KING R7..."
python3 "$ENGINE"
