cat > bdking_r7_ultra.sh << 'EOF'
#!/bin/sh
# ===============================
# BD-KING-R7 POWERHUB ULTRA SYSTEM
# Version: #1638
# ===============================

ROOT="$HOME/Tamanna"
LOG="$ROOT/powerhub_ultra.log"

echo "=== BD-KING-R7 POWERHUB ULTRA START ===" > "$LOG"

# 1️⃣ Check folder
if [ ! -d "$ROOT" ]; then
    echo "Folder $ROOT not found!" | tee -a "$LOG"
    exit 1
fi

cd "$ROOT" || exit
echo "Running in $(pwd)" | tee -a "$LOG"

# 2️⃣ Fix Shell scripts permissions
find . -type f -name "*.sh" -exec chmod +x {} \;

# 3️⃣ Install dependencies
echo "Installing core dependencies..." | tee -a "$LOG"
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 curl wget nano 2>>"$LOG"

# 4️⃣ Run Python files
for f in $(find . -type f -name "*.py"); do
    echo "[PY] Running $f" | tee -a "$LOG"
    python3 "$f" >>"$LOG" 2>&1 || echo "[PY] ERROR in $f" | tee -a "$LOG"
done

# 5️⃣ Run NodeJS files
for f in $(find . -type f -name "*.js"); do
    echo "[NODE] Running $f" | tee -a "$LOG"
    node "$f" >>"$LOG" 2>&1 || echo "[NODE] ERROR in $f" | tee -a "$LOG"
done

# 6️⃣ Run Shell scripts
for f in $(find . -type f -name "*.sh"); do
    echo "[SH] Running $f" | tee -a "$LOG"
    sh "$f" >>"$LOG" 2>&1 || echo "[SH] ERROR in $f" | tee -a "$LOG"
done

# 7️⃣ Compile & Run C files
for f in $(find . -type f -name "*.c"); do
    out="${f%.c}"
    echo "[C] Compiling $f" | tee -a "$LOG"
    gcc "$f" -o "$out" && ./"$out" >>"$LOG" 2>&1 || echo "[C] ERROR in $f" | tee -a "$LOG"
done

# 8️⃣ Compile & Run Java files
for f in $(find . -type f -name "*.java"); do
    cls=$(basename "$f" .java)
    echo "[JAVA] Compiling $f" | tee -a "$LOG"
    javac "$f" 2>>"$LOG" && java "$cls" >>"$LOG" 2>&1 || echo "[JAVA] ERROR in $f" | tee -a "$LOG"
done

# 9️⃣ GitHub Backup
echo "GitHub Backup..." | tee -a "$LOG"
git add .
git commit -m "POWERHUB ULTRA auto backup $(date)" >>"$LOG" 2>&1

read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "Push failed! Check $LOG" | tee -a "$LOG"

echo "=== BD-KING-R7 POWERHUB ULTRA COMPLETE ===" | tee -a "$LOG"
echo "Check full log: $LOG"
EOF