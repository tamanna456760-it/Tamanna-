cat > tamanna_debug.sh << 'EOF'
#!/bin/sh
set -x

ROOT="$HOME/Tamanna"
LOG="$ROOT/debug_run.log"

echo "===== DEBUG START =====" > "$LOG"

if [ ! -d "$ROOT" ]; then
  echo "Tamanna folder not found at $ROOT" | tee -a "$LOG"
  exit 1
fi

cd "$ROOT" || exit

echo "Current dir: $(pwd)" | tee -a "$LOG"
echo "Files:" | tee -a "$LOG"
ls -lah >> "$LOG" 2>&1

echo "Installing tools..." | tee -a "$LOG"
apk add --no-cache python3 nodejs npm bash gcc g++ make openjdk17 2>>"$LOG"

echo "Running python files" | tee -a "$LOG"
for f in *.py; do
  [ -f "$f" ] && python3 "$f" >>"$LOG" 2>&1
done

echo "Running node files" | tee -a "$LOG"
for f in *.js; do
  [ -f "$f" ] && node "$f" >>"$LOG" 2>&1
done

echo "Running shell files" | tee -a "$LOG"
for f in *.sh; do
  [ -f "$f" ] && sh "$f" >>"$LOG" 2>&1
done

echo "Trying build" | tee -a "$LOG"
[ -f Makefile ] && make >>"$LOG" 2>&1

echo "Git backup" | tee -a "$LOG"
git add . >>"$LOG" 2>&1
git commit -m "debug backup" >>"$LOG" 2>&1

echo "===== DEBUG END =====" | tee -a "$LOG"
EOF