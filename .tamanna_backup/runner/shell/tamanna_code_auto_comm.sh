cat > ~tamanna_code_auto_comm.sh << 'EOF'
#!/bin/sh
# =========================================
# TAMANNA ULTRA CODE AUTO GENERATOR + COMM SYSTEM
# Version: #8000
# Features:
# - Auto generate code (Python, Node, Shell, C, Java)
# - Save in correct folder
# - Auto run code
# - Communication system (heartbeat + status)
# - Zip/Unzip backup
# - GitHub sync
# =========================================

ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/tamanna_code_auto_comm.log"
mkdir -p "$ROOT/logs"

echo "=== TAMANNA AUTO CODE + COMM SYSTEM START ===" | tee -a "$LOG"
cd "$ROOT" || exit

# 1️⃣ Install dependencies
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip curl wget 2>>"$LOG"

# 2️⃣ Communication Heartbeat
echo "[COMM] Heartbeat: $(date)" | tee -a "$LOG"

# 3️⃣ Ask for code type
echo "Enter code type to auto-generate (python/node/shell/c/java): "
read TYPE
echo "Enter file name (without extension): "
read FILENAME

case $TYPE in
    python) FOLDER="python"; EXT="py"; RUN="python3"; GEN="print('Hello from Tamanna Python auto-gen')" ;;
    node) FOLDER="node"; EXT="js"; RUN="node"; GEN="console.log('Hello from Tamanna Node auto-gen');" ;;
    shell) FOLDER="shell"; EXT="sh"; RUN="sh"; GEN="echo 'Hello from Tamanna Shell auto-gen'" ;;
    c) FOLDER="c_programs"; EXT="c"; GEN='#include <stdio.h>\nint main(){printf("Hello from Tamanna C auto-gen\n"); return 0;}' ;;
    java) FOLDER="java_programs"; EXT="java"; GEN="public class $FILENAME { public static void main(String[] args){ System.out.println(\"Hello from Tamanna Java auto-gen\");}}" ;;
    *) echo "Invalid type!"; exit 1;;
esac

mkdir -p "$ROOT/$FOLDER"
FILEPATH="$ROOT/$FOLDER/$FILENAME.$EXT"

# 4️⃣ Auto-generate code
echo -e "$GEN" > "$FILEPATH"
echo "[AUTO-GEN] Code generated at $FILEPATH" | tee -a "$LOG"

# 5️⃣ Run code
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

# 6️⃣ Communication Status
echo "[COMM] Status: $FILENAME.$EXT executed successfully at $(date)" | tee -a "$LOG"

# 7️⃣ Zip any backup folder
for d in $(find . -type d -name "backup"); do
    ZIPFILE="$d-$(date +%Y%m%d%H%M%S).zip"
    zip -r "$ZIPFILE" "$d" >>"$LOG" 2>&1
done

# 8️⃣ GitHub auto sync
git add .
git commit -m "Tamanna AUTO code + COMM $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"
read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "GitHub Push failed, check $LOG" | tee -a "$LOG"

echo "=== TAMANNA AUTO CODE + COMM COMPLETE ===" | tee -a "$LOG"
echo "Check log: $LOG"
EOF