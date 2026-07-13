cat > tamanna_runner.sh << 'EOF'
#!/bin/sh
# =========================
# TAMANNA UNIVERSAL TERMINAL RUNNER
# =========================

ROOT="$HOME/Tamanna"
LOG="$ROOT/run_terminal.log"

echo "==== TAMANNA TERMINAL RUNNER START ====" > "$LOG"

# 1️⃣ Check folder
if [ ! -d "$ROOT" ]; then
    echo "Folder $ROOT not found!" | tee -a "$LOG"
    exit 1
fi

cd "$ROOT" || exit
echo "Running in $(pwd)" | tee -a "$LOG"

# 2️⃣ Fix shell scripts
find . -type f -name "*.sh" -exec chmod +x {} \;

# 3️⃣ Install dependencies
echo "Installing basic dependencies..." | tee -a "$LOG"
apk add --no-cache python3 py3-pip nodejs npm bash gcc g++ make openjdk17 2>>"$LOG"

# 4️⃣ Python run
for f in $(find . -type f -name "*.py"); do
    echo "[PY] Running $f" | tee -a "$LOG"
    python3 "$f" >>"$LOG" 2>&1 || echo "[PY] ERROR in $f" | tee -a "$LOG"
done

# 5️⃣ NodeJS run
for f in $(find . -type f -name "*.js"); do
    echo "[NODE] Running $f" | tee -a "$LOG"
    node "$f" >>"$LOG" 2>&1 || echo "[NODE] ERROR in $f" | tee -a "$LOG"
done

# 6️⃣ Shell run
for f in $(find . -type f -name "*.sh"); do
    echo "[SH] Running $f" | tee -a "$LOG"
    sh "$f" >>"$LOG" 2>&1 || echo "[SH] ERROR in $f" | tee -a "$LOG"
done

# 7️⃣ C compile & run
for f in $(find . -type f -name "*.c"); do
    out="${f%.c}"
    echo "[C] Compiling $f" | tee -a "$LOG"
    gcc "$f" -o "$out" 2>>"$LOG" && ./"$out" >>"$LOG" 2>&1 || echo "[C] ERROR in $f" | tee -a "$LOG"
done

# 8️⃣ Java compile & run
for f in $(find . -type f -name "*.java"); do
    cls=$(basename "$f" .java)
    echo "[JAVA] Compiling $f" | tee -a "$LOG"
    javac "$f" 2>>"$LOG" && java "$cls" >>"$LOG" 2>&1 || echo "[JAVA] ERROR in $f" | tee -a "$LOG"
done

echo "==== RUN COMPLETE ====" | tee -a "$LOG"
echo "Check log: $LOG"
EOF