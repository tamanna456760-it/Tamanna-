mkdir -p ~/Tamanna/scripts ~/Tamanna/python ~/Tamanna/node ~/Tamanna/shell ~/Tamanna/c_programs ~/Tamanna/java_programs ~/Tamanna/zip_backups ~/Tamanna/logs

cat > ~/Tamanna/scripts/tamanna_ultra_extreme.sh << 'EOF'
#!/bin/sh
# =============================================
# FULL EXTREME BD-KING-R7 TAMANNA ULTRA SYSTEM
# Features:
# - Auto run all code (Python/Node/Shell/C/Java)
# - Unlimited dynamic firewall
# - Auto backup zip/unzip
# - GitHub auto push
# - Heartbeat + logs
# - Web Dashboard
# - Mobile/Telegram/Email Alerts
# - Multi-device & Multi-server cloud sync
# =============================================

ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/ultra_extreme.log"
mkdir -p "$ROOT/logs"

echo "=== ULTRA EXTREME SYSTEM START ===" > "$LOG"
cd "$ROOT" || exit

# 1️⃣ Install all dependencies
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip curl wget iptables socat rsync mailx jq 2>>"$LOG"

# 2️⃣ Harden folders
find . -type d -exec chmod 700 {} \;
find . -type f -exec chmod 600 {} \;

# 3️⃣ Auto generate Python secure token
GEN_PY="$ROOT/python/secure_auto_$(date +%s).py"
echo "import secrets, hashlib; print('Secure Token:', hashlib.sha256(secrets.token_bytes(32)).hexdigest())" > "$GEN_PY"
echo "[AUTO GEN] Python secure code: $GEN_PY" | tee -a "$LOG"

# 4️⃣ Run all code
for TYPE in python node shell c_programs java_programs; do
    for f in $(find "./$TYPE" -type f 2>/dev/null); do
        echo "[RUN] $f" | tee -a "$LOG"
        case $TYPE in
            python) python3 "$f" >>"$LOG" 2>&1 || echo "[ERROR] $f failed" | tee -a "$LOG";;
            node) node "$f" >>"$LOG" 2>&1 || echo "[ERROR] $f failed" | tee -a "$LOG";;
            shell) sh "$f" >>"$LOG" 2>&1 || echo "[ERROR] $f failed" | tee -a "$LOG";;
            c_programs) OUT="${f%.c}.out"; gcc "$f" -o "$OUT" && "$OUT" >>"$LOG" 2>&1 || echo "[ERROR] $f failed" | tee -a "$LOG";;
            java_programs) cls=$(basename "$f" .java); javac "$f" -d ./java_programs 2>>"$LOG" && java -cp ./java_programs "$cls" >>"$LOG" 2>&1 || echo "[ERROR] $f failed" | tee -a "$LOG";;
        esac
    done
done

# 5️⃣ Firewall unlimited dynamic rules
iptables -F; iptables -X
iptables -P INPUT DROP; iptables -P FORWARD DROP; iptables -P OUTPUT ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
for ip in $(cat "$ROOT/attack_ips.txt" 2>/dev/null); do iptables -A INPUT -s $ip -j DROP; done
iptables-save > "$ROOT/logs/firewall_rules_$(date +%Y%m%d%H%M%S).txt"

# 6️⃣ Auto backup zip/unzip
for d in $(find . -type d -name "backup"); do
    ZIPFILE="$ROOT/zip_backups/$(basename $d)-$(date +%Y%m%d%H%M%S).zip"
    zip -r "$ZIPFILE" "$d" >>"$LOG" 2>&1
done

# 7️⃣ GitHub auto push
git add .
git commit -m "ULTRA EXTREME AUTO $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"
read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "GitHub Push failed" | tee -a "$LOG"

# 8️⃣ Heartbeat + Terminal + Email/Telegram Alerts
ALERT_MSG="Tamanna BD-KING-R7 ULTRA EXTREME RUN at $(date)"
echo "[COMM] $ALERT_MSG" | tee -a "$LOG"

# Telegram alert
TELEGRAM_TOKEN="YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" -d chat_id="$TELEGRAM_CHAT_ID" -d text="$ALERT_MSG" >>"$LOG" 2>&1

# Email alert
if command -v mailx >/dev/null 2>&1; then
    echo "$ALERT_MSG" | mailx -s "Tamanna ULTRA EXTREME ALERT" your_email@example.com
fi

# 9️⃣ Web Dashboard
echo "<h1>TAMANA BD-KING-R7 ULTRA EXTREME STATUS</h1><p>Last run: $(date)</p>" > ~/Tamanna/index.html
socat TCP-LISTEN:8080,fork FILE:~/Tamanna/index.html &

# 🔹 Multi-device & Multi-server sync placeholder (rsync)
# rsync -avz ~/Tamanna username@remote_server:/path/to/tamanna_backup

echo "=== ULTRA EXTREME SYSTEM COMPLETE ===" | tee -a "$LOG"
echo "Check log: $LOG"
echo "Web Dashboard running at http://localhost:8080"
EOF