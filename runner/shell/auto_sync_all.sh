cat > ~auto_sync_all.sh << 'EOF'
#!/bin/sh
# ===============================================
# TAMANNA BD-KING-R7 ULTRA + AUTO SYNC SYSTEM
# Features:
# - Scan all code folders
# - Run Python/Node/Shell/C/Java
# - Auto backup zip/unzip
# - GitHub commit & push automatically
# - Logs all activities
# ===============================================

ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/auto_sync_all.log"
mkdir -p "$ROOT/logs"

echo "=== AUTO SYNC SYSTEM START ===" > "$LOG"
cd "$ROOT" || exit

# 1️⃣ Install dependencies
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip curl wget 2>>"$LOG"

# 2️⃣ Backup any 'backup' folders
for d in $(find . -type d -name "backup"); do
    ZIPFILE="$ROOT/zip_backups/$(basename $d)-$(date +%Y%m%d%H%M%S).zip"
    mkdir -p "$ROOT/zip_backups"
    zip -r "$ZIPFILE" "$d" >>"$LOG" 2>&1 || echo "[ZIP] ERROR $ZIPFILE" | tee -a "$LOG"
done

# 3️⃣ Run all code
for TYPE in python node shell c_programs java_programs; do
    for f in $(find "./$TYPE" -type f); do
        EXT="${f##*.}"
        echo "[RUN] $f" | tee -a "$LOG"
        case $TYPE in
            python) python3 "$f" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
            node) node "$f" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
            shell) sh "$f" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
            c_programs)
                OUT="${f%.c}.out"
                gcc "$f" -o "$OUT" && "$OUT" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
            java_programs)
                cls=$(basename "$f" .java)
                javac "$f" -d ./java_programs 2>>"$LOG" && java -cp ./java_programs "$cls" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
        esac
    done
done

# 4️⃣ GitHub Auto Commit & Push
git add .
git commit -m "AUTO SYNC RUN $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"

# GitHub credentials
read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "GitHub Push failed, check $LOG" | tee -a "$LOG"

# 5️⃣ Heartbeat / Communication log
echo "[COMM] Heartbeat: $(date) | All code scanned & synced" | tee -a "$LOG"

echo "=== AUTO SYNC SYSTEM COMPLETE ===" | tee -a "$LOG"
echo "Check log: $LOG"
EOF