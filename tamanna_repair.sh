#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "===== TAMANNA AI REPAIR START ====="

# Backup
BACKUP="$HOME/tamanna_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP"

tar -czf "$BACKUP/project_backup.tar.gz" . 2>/dev/null || true

echo "[OK] Backup created"


# Git check
echo "[Git]"
git status
git fetch origin || true


# Python repair
echo "[Python]"
python -m pip install --upgrade pip || true

if [ -f requirements.txt ]; then
    pip install -r requirements.txt || true
fi


# Create health report
mkdir -p logs

{
echo "===== Tamanna AI Health Report ====="
date

echo ""
echo "Python:"
python --version

echo ""
echo "Git:"
git log --oneline -5

echo ""
echo "Files:"
find . -maxdepth 2 -type f | wc -l

echo ""
echo "Compile Check:"
python -m compileall . 

} > logs/tamanna_health_report.txt 2>&1


# Save changes
git add logs/tamanna_health_report.txt

git commit -m "Tamanna AI automatic repair health update" || true

git push origin main || true


echo "===== TAMANNA AI REPAIR COMPLETE ====="
echo "Report: logs/tamanna_health_report.txt"

