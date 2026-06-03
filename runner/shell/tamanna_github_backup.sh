cat > tamanna_github_backup.sh << 'EOF'
#!/bin/sh
# ===============================
# TAMANNA GITHUB AUTO BACKUP SCRIPT
# ===============================

ROOT="$HOME/Tamanna"
LOG="$ROOT/run_report.log"

echo "==== TAMANNA BACKUP & RUN ====" > "$LOG"

# 1️⃣ check folder
if [ ! -d "$ROOT" ]; then
    echo "Folder $ROOT not found" | tee -a "$LOG"
    exit 1
fi

cd "$ROOT" || exit

# 2️⃣ show current files
echo "Files in folder:" | tee -a "$LOG"
ls -lah >>"$LOG" 2>&1

# 3️⃣ fix permissions for shell scripts
find . -type f -name "*.sh" -exec chmod +x {} \;

# 4️⃣ install basic deps
echo "Installing dependencies..." | tee -a "$LOG"
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 2>>"$LOG"

# 5️⃣ run Python files (safe)
for f in *.py; do
  [ -f "$f" ] && echo "Running $f" | tee -a "$LOG" && python3 "$f" >>"$LOG" 2>&1 || echo "Failed $f" | tee -a "$LOG"
done

# 6️⃣ run NodeJS files (safe)
for f in *.js; do
  [ -f "$f" ] && echo "Running $f" | tee -a "$LOG" && node "$f" >>"$LOG" 2>&1 || echo "Failed $f" | tee -a "$LOG"
done

# 7️⃣ run Shell scripts (safe)
for f in *.sh; do
  [ -f "$f" ] && echo "Running $f" | tee -a "$LOG" && sh "$f" >>"$LOG" 2>&1 || echo "Failed $f" | tee -a "$LOG"
done

# 8️⃣ Git commit & push
echo "Git backup..." | tee -a "$LOG"
git add .
git commit -m "Auto backup $(date)" >>"$LOG" 2>&1

# Push to GitHub
read -p "Enter GitHub Username: " USER
read -sp "Enter GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1

echo "==== DONE ====" | tee -a "$LOG"
echo "Check log at $LOG"
EOF