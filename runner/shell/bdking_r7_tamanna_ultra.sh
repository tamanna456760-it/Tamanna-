cat > ~bdking_r7_tamanna_ultra.sh << 'EOF'
#!/bin/sh
# =====================================
# BD-KING-R7 + TAMANNA ULTRA ALL-IN-ONE
# Version: #7000
# Features:
# - All code language support (Python, NodeJS, Shell, C, Java)
# - Auto scan, run, fix, log
# - Zip/Unzip backups
# - GitHub auto sync
# - BD-KING-R7 system integration
# =====================================

ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/bdking_r7_ultra.log"

mkdir -p "$ROOT/logs"
echo "=== BD-KING-R7 + TAMANNA ULTRA START ===" > "$LOG"

cd "$ROOT" || exit

# 1️⃣ Install dependencies
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip curl wget 2>>"$LOG"

# 2️⃣ Auto unzip .zip files
for f in $(find . -type f -name "*.zip"); do
    echo "[ZIP] Unzipping $f" | tee -a "$LOG"
    unzip -o "$f" -d "$(dirname "$f")" >>"$LOG" 2>&1 || echo "[ZIP] ERROR $f" | tee -a "$LOG"
done

# 3️⃣ Backup any 'backup' folder
for d in $(find . -type d -name "backup"); do
    ZIPFILE="$d-$(date +%Y%m%d%H%M%S).zip"
    echo "[ZIP] Backup $ZIPFILE" | tee -a "$LOG"
    zip -r "$ZIPFILE" "$d" >>"$LOG" 2>&1 || echo "[ZIP] ERROR $ZIPFILE" | tee -a "$LOG"
done

# 4️⃣ Scan all files and generate info
echo "--- FILE INFO ---" | tee -a "$LOG"
for f in $(find . -type f); do
    SIZE=$(stat -c%s "$f")
    LINES=$(wc -l < "$f" 2>/dev/null || echo 0)
    MODIFIED=$(stat -c%y "$f")
    EXT="${f##*.}"
    echo "File: $f | Size: $SIZE | Lines: $LINES | Modified: $MODIFIED | Type: $EXT" | tee -a "$LOG"
done

# 5️⃣ Fix shell permissions
find . -type f -name "*.sh" -exec chmod +x {} \;

# 6️⃣ Run Python
for f in $(find ./python -type f -name "*.py"); do
    echo "[PY] Running $f" | tee -a "$LOG"
    python3 "$f" >>"$LOG" 2>&1 || echo "[PY] ERROR $f" | tee -a "$LOG"
done

# 7️⃣ Run NodeJS
for f in $(find ./node -type f -name "*.js"); do
    echo "[NODE] Running $f" | tee -a "$LOG"
    node "$f" >>"$LOG" 2>&1 || echo "[NODE] ERROR $f" | tee -a "$LOG"
done

# 8️⃣ Run Shell scripts
for f in $(find ./shell -type f -name "*.sh"); do
    echo "[SH] Running $f" | tee -a "$LOG"
    sh "$f" >>"$LOG" 2>&1 || echo "[SH] ERROR $f" | tee -a "$LOG"
done

# 9️⃣ Compile & run C programs
for f in $(find ./c_programs -type f -name "*.c"); do
    OUT="$ROOT/c_programs/$(basename "$f" .c).out"
    gcc "$f" -o "$OUT" && "$OUT" >>"$LOG" 2>&1 || echo "[C] ERROR $f" | tee -a "$LOG"
done

# 🔟 Compile & run Java programs
for f in $(find ./java_programs -type f -name "*.java"); do
    cls=$(basename "$f" .java)
    javac "$f" -d ./java_programs 2>>"$LOG" && java -cp ./java_programs "$cls" >>"$LOG" 2>&1 || echo "[JAVA] ERROR $f" | tee -a "$LOG"
done

# 1️⃣1️⃣ GitHub auto sync
echo "GitHub auto sync..." | tee -a "$LOG"
git add .
git commit -m "BD-KING-R7 ULTRA auto backup $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"

read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "GitHub Push failed, check $LOG" | tee -a "$LOG"

echo "=== BD-KING-R7 + TAMANNA ULTRA COMPLETE ===" | tee -a "$LOG"
echo "Check log: $LOG"
EOF