cat > tamanna_ultra_powerhub.sh << 'EOF'
#!/bin/sh
# ===============================
# TAMANNA ULTRA POWERHUB
# Version: #5000
# Features: File scan, zip/unzip, code run/fix, GitHub sync
# ===============================

ROOT="$HOME/Tamanna"
LOG="$ROOT/ultra_powerhub.log"

echo "=== TAMANNA ULTRA POWERHUB START ===" > "$LOG"

# 1️⃣ Check root folder
if [ ! -d "$ROOT" ]; then
    echo "Folder $ROOT not found!" | tee -a "$LOG"
    exit 1
fi

cd "$ROOT" || exit
echo "Working in $(pwd)" | tee -a "$LOG"

# 2️⃣ Install dependencies
echo "Installing core dependencies..." | tee -a "$LOG"
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 curl wget nano zip unzip 2>>"$LOG"

# 3️⃣ Auto unzip any .zip files
for f in $(find . -type f -name "*.zip"); do
    echo "[ZIP] Unzipping $f" | tee -a "$LOG"
    unzip -o "$f" -d "$(dirname "$f")" >>"$LOG" 2>&1 || echo "[ZIP] ERROR unzipping $f" | tee -a "$LOG"
done

# 4️⃣ Auto zip backup any folder named 'backup'
for d in $(find . -type d -name "backup"); do
    ZIPFILE="$d-$(date +%Y%m%d%H%M%S).zip"
    echo "[ZIP] Creating backup zip $ZIPFILE" | tee -a "$LOG"
    zip -r "$ZIPFILE" "$d" >>"$LOG" 2>&1 || echo "[ZIP] ERROR creating $ZIPFILE" | tee -a "$LOG"
done

# 5️⃣ File info report
echo "--- FILE INFO REPORT ---" | tee -a "$LOG"
for f in $(find . -type f); do
    SIZE=$(stat -c%s "$f")
    LINES=$(wc -l < "$f" 2>/dev/null || echo 0)
    MODIFIED=$(stat -c%y "$f")
    EXT="${f##*.}"
    echo "File: $f | Size: $SIZE bytes | Lines: $LINES | Modified: $MODIFIED | Type: $EXT" | tee -a "$LOG"
done

# 6️⃣ Fix shell script permissions
find . -type f -name "*.sh" -exec chmod +x {} \;

# 7️⃣ Run Python
for f in $(find . -type f -name "*.py"); do
    echo "[PY] Running $f" | tee -a "$LOG"
    python3 "$f" >>"$LOG" 2>&1 || echo "[PY] ERROR in $f" | tee -a "$LOG"
done

# 8️⃣ Run NodeJS
for f in $(find . -type f -name "*.js"); do
    echo "[NODE] Running $f" | tee -a "$LOG"
    node "$f" >>"$LOG" 2>&1 || echo "[NODE] ERROR in $f" | tee -a "$LOG"
done

# 9️⃣ Run Shell scripts
for f in $(find . -type f -name "*.sh"); do
    echo "[SH] Running $f" | tee -a "$LOG"
    sh "$f" >>"$LOG" 2>&1 || echo "[SH] ERROR in $f" | tee -a "$LOG"
done

# 🔟 Compile & Run C
for f in $(find . -type f -name "*.c"); do
    out="${f%.c}"
    echo "[C] Compiling $f" | tee -a "$LOG"
    gcc "$f" -o "$out" && ./"$out" >>"$LOG" 2>&1 || echo "[C] ERROR in $f" | tee -a "$LOG"
done

# 1️⃣1️⃣ Compile & Run Java
for f in $(find . -type f -name "*.java"); do
    cls=$(basename "$f" .java)
    echo "[JAVA] Compiling $f" | tee -a "$LOG"
    javac "$f" 2>>"$LOG" && java "$cls" >>"$LOG" 2>&1 || echo "[JAVA] ERROR in $f" | tee -a "$LOG"
done

# 1️⃣2️⃣ GitHub Auto Backup
echo "GitHub auto sync..." | tee -a "$LOG"
git add .
git commit -m "ULTRA POWERHUB auto backup $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"

read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "GitHub Push failed, check $LOG" | tee -a "$LOG"

echo "=== TAMANNA ULTRA POWERHUB COMPLETE ===" | tee -a "$LOG"
echo "Check log at: $LOG"
EOF