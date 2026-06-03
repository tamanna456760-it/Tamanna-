cat > ~tamanna_code_editor_runner.sh << 'EOF'
#!/bin/sh
# =====================================
# TAMANNA ULTRA CODE EDITOR + RUNNER + SYNC
# Version: #6000
# Features:
# - Create/Edit code
# - Save in correct folder
# - Run automatically
# - GitHub sync
# =====================================

ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/code_editor_runner.log"
mkdir -p "$ROOT/logs"

echo "=== TAMANNA CODE EDITOR + RUNNER START ===" | tee -a "$LOG"

# 1️⃣ Install dependencies
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip 2>>"$LOG"

# 2️⃣ Prompt user for code info
echo "Enter code type (python/node/shell/c/java): "
read TYPE
echo "Enter file name (without extension): "
read FILENAME

# 3️⃣ Determine folder & extension
case $TYPE in
    python) FOLDER="python"; EXT="py"; RUN="python3";;
    node) FOLDER="node"; EXT="js"; RUN="node";;
    shell) FOLDER="shell"; EXT="sh"; RUN="sh";;
    c) FOLDER="c_programs"; EXT="c"; RUN="gcc";;
    java) FOLDER="java_programs"; EXT="java"; RUN="java";;
    *) echo "Invalid type!"; exit 1;;
esac

# 4️⃣ Create folder if not exists
mkdir -p "$ROOT/$FOLDER"

FILEPATH="$ROOT/$FOLDER/$FILENAME.$EXT"

# 5️⃣ Open nano editor
echo "Opening editor for $FILEPATH"
nano "$FILEPATH"

# 6️⃣ Run code
echo "[RUN] Executing $FILEPATH" | tee -a "$LOG"
case $TYPE in
    python|node|shell)
        $RUN "$FILEPATH" >>"$LOG" 2>&1 || echo "[ERROR] $FILEPATH failed" | tee -a "$LOG";;
    c)
        OUT="$ROOT/$FOLDER/$FILENAME.out"
        gcc "$FILEPATH" -o "$OUT" && "$OUT" >>"$LOG" 2>&1 || echo "[ERROR] $FILEPATH failed" | tee -a "$LOG";;
    java)
        javac "$FILEPATH" -d "$ROOT/$FOLDER" 2>>"$LOG" && java -cp "$ROOT/$FOLDER" "$FILENAME" >>"$LOG" 2>&1 || echo "[ERROR] $FILEPATH failed" | tee -a "$LOG";;
esac

# 7️⃣ GitHub sync
echo "GitHub auto sync..." | tee -a "$LOG"
cd "$ROOT"
git add .
git commit -m "Code added/edited: $FILENAME.$EXT $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"

read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "GitHub Push failed, check $LOG" | tee -a "$LOG"

echo "=== TAMANNA CODE EDITOR + RUNNER COMPLETE ===" | tee -a "$LOG"
echo "Check log at $LOG"
EOF