cat > tamanna_ultra_fileinfo.sh << 'EOF'
#!/bin/sh
# ===============================
# TAMANNA ULTRA FILE INFO + RUN + SYNC
# Version: #4000
# ===============================

ROOT="$HOME/Tamanna"
LOG="$ROOT/ultra_fileinfo.log"

echo "=== TAMANNA ULTRA START ===" > "$LOG"

# 1️⃣ Check if folder exists
if [ ! -d "$ROOT" ]; then
    echo "Folder $ROOT not found!" | tee -a "$LOG"
    exit 1
fi

cd "$ROOT" || exit
echo "Working in $(pwd)" | tee -a "$LOG"

# 2️⃣ File Info Report
echo "--- FILE INFO REPORT ---" | tee -a "$LOG"
for f in $(find . -type f); do
    SIZE=$(stat -c%s "$f")
    LINES=$(wc -l < "$f" 2>/dev/null || echo 0)
    MODIFIED=$(stat -c%y "$f")
    EXT="${f##*.}"
    echo "File: $f | Size: $SIZE bytes | Lines: $LINES | Modified: $MODIFIED | Type: $EXT" | tee -a "$LOG"
done

# 3️⃣ Fix Shell script permissions
find . -type f -name "*.sh" -exec chmod +x {} \;

# 4️⃣ Install dependencies
echo "Installing core dependencies..." | tee -a "$LOG"
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 curl wget nano 2>>"$LOG"

# 5️⃣ Run Python
for f in $(find . -type f -name "*.py"); do
    echo "[PY] Running $f" | tee -a "$LOG"
    python3 "$f" >>"$LOG" 2>&1 || echo "[PY] ERROR in $f" | tee -a "$LOG"
done

# 6️⃣ Run NodeJS
for f in $(find . -type f -name "*.js"); do
    echo "[NODE] Running $f" | tee -a "$LOG"
    node "$f" >>"$LOG" 2>&1 || echo "[NODE] ERROR in $f" | tee -a "$LOG"
done

# 7️⃣ Run Shell scripts
for f in $(find . -type f -name "*.sh"); do
    echo "[SH] Running $f" | tee -a "$LOG"
    sh "$f" >>"$LOG" 2>&1 || echo "[SH] ERROR in $f" | tee -a "$LOG"
done

# 8️⃣ Compile & Run C
for f in $(find . -type f -name "*.c"); do
    out="${f%.c}"
    echo "[C] Compiling $f" | tee -a "$LOG"
    gcc "$f" -o "$out" && ./"$out" >>"$LOG" 2>&1 || echo "[C] ERROR in $f" | tee -a "$LOG"
done

# 9️⃣ Compile & Run Java
for f in $(find . -type f -name "*.java"); do
    cls=$(basename "$f" .java)
    echo "[JAVA] Compiling $f" | tee -a "$LOG"
    javac "$f" 2>>"$LOG" && java "$cls" >>"$LOG" 2>&1 || echo "[JAVA] ERROR in $f" | tee -a "$LOG"
done

# 🔟 GitHub Auto Backup
echo "GitHub auto sync..." | tee -a "$LOG"
git add .
git commit -m "ULTRA FILE INFO auto backup $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"

read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "GitHub Push failed, check $LOG" | tee -a "$LOG"

echo "=== TAMANNA ULTRA COMPLETE ===" | tee -a "$LOG"
echo "Check log: $LOG"
EOF