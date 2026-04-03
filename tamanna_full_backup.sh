cat > tamanna_full_backup.sh << 'EOF'
#!/bin/sh
# ===============================
# TAMANNA FULL GITHUB BACKUP
# ===============================

ROOT="$HOME/Tamanna"
LOG="$ROOT/github_backup.log"

echo "==== TAMANNA FULL GITHUB BACKUP ====" > "$LOG"

# 1️⃣ Check folder
if [ ! -d "$ROOT" ]; then
    echo "Folder $ROOT not found!" | tee -a "$LOG"
    exit 1
fi

cd "$ROOT" || exit

# 2️⃣ Show files
echo "Files in folder:" | tee -a "$LOG"
ls -lah >>"$LOG" 2>&1

# 3️⃣ Fix permissions
find . -type f -name "*.sh" -exec chmod +x {} \;

# 4️⃣ Install git if missing
apk add --no-cache git 2>>"$LOG"

# 5️⃣ Initialize git if not
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

# 6️⃣ Add all files
git add . >>"$LOG" 2>&1

# 7️⃣ Commit
git commit -m "Auto backup $(date)" >>"$LOG" 2>&1

# 8️⃣ Setup remote
read -p "Enter GitHub Username: " USER
read -sp "Enter GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git

# 9️⃣ Push
git push -u origin main >>"$LOG" 2>&1 || echo "Push failed! Check $LOG"

echo "==== DONE ====" | tee -a "$LOG"
echo "All files backup log: $LOG"
EOF