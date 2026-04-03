cat > tamanna_power.sh << 'EOF'
#!/bin/sh

echo "==== TAMANNA POWER ENGINE ===="

ROOT="$HOME/Tamanna"
LOG="$ROOT/run_report.log"

cd "$ROOT" || exit

echo "Start time: $(date)" > "$LOG"

run_py() {
  echo "[PY] $1" | tee -a "$LOG"
  python3 "$1" >>"$LOG" 2>&1 &
}

run_js() {
  echo "[NODE] $1" | tee -a "$LOG"
  node "$1" >>"$LOG" 2>&1 &
}

run_sh() {
  echo "[SH] $1" | tee -a "$LOG"
  sh "$1" >>"$LOG" 2>&1 &
}

compile_c() {
  out="${1%.c}"
  gcc "$1" -o "$out" 2>>"$LOG" && ./"$out" &
}

compile_java() {
  javac "$1" 2>>"$LOG"
  cls=$(basename "$1" .java)
  java "$cls" >>"$LOG" 2>&1 &
}

echo "Scanning files..."

for f in $(find . -type f); do
  case "$f" in
    *.py) run_py "$f" ;;
    *.js) run_js "$f" ;;
    *.sh) chmod +x "$f"; run_sh "$f" ;;
    *.c) compile_c "$f" ;;
    *.java) compile_java "$f" ;;
  esac
done

echo "Installing deps..."
[ -f requirements.txt ] && pip3 install -r requirements.txt >>"$LOG" 2>&1
[ -f package.json ] && npm install >>"$LOG" 2>&1
[ -f Makefile ] && make >>"$LOG" 2>&1

echo "Git backup..."
git add .
git commit -m "auto run backup $(date)" >>"$LOG" 2>&1

echo "DONE"
EOF