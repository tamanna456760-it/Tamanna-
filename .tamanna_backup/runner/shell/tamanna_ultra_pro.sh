mkdir -p ~/Tamanna/{scripts,python,node,shell,java_programs,c_programs,zip_backups,logs}

cat > ~/Tamanna/scripts/tamanna_ultra_pro.sh << 'EOF'
#!/bin/sh
# TAMANNA ULTRA PRO SYSTEM
ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/tamanna_pro.log"
mkdir -p "$ROOT/logs"

echo "[START] $(date)" > "$LOG"
cd "$ROOT" || exit

# 1️⃣ Dependencies
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip curl iptables socat rsync mailx jq 2>>"$LOG"

# 2️⃣ Harden files
find . -type d -exec chmod 700 {} \;
find . -type f -exec chmod 600 {} \;

# 3️⃣ Auto generate Python secure token
GEN_PY="$ROOT/python/secure_auto_$(date +%s).py"
echo "import secrets, hashlib; print('Secure Token:', hashlib.sha256(secrets.token_bytes(32)).hexdigest())" > "$GEN_PY"

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

# 5️⃣ Firewall
iptables -F; iptables -X
iptables -P INPUT DROP; iptables -P FORWARD DROP; iptables -P OUTPUT ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
for ip in $(cat "$ROOT/attack_ips.txt" 2>/dev/null); do iptables -A INPUT -s $ip -j DROP; done

# 6️⃣ Auto Backup
for d in $(find . -type d -name "backup"); do
    ZIP="$ROOT/zip_backups/$(basename $d)-$(date +%Y%m%d%H%M%S).zip"
    zip -r "$ZIP" "$d" >>"$LOG" 2>&1
done

# 7️⃣ GitHub Push
git add .
git commit -m "ULTRA PRO AUTO $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit"
read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "[ERROR] GitHub push failed"

# 8️⃣ Heartbeat & Alerts
ALERT="Tamanna ULTRA PRO ran at $(date)"
echo "[HEARTBEAT] $ALERT" | tee -a "$LOG"
curl -s -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" -d chat_id=YOUR_CHAT_ID -d text="$ALERT" >>"$LOG" 2>&1
echo "$ALERT" | mailx -s "Tamanna ULTRA PRO ALERT" your_email@example.com

# 9️⃣ Dashboard
echo "<h1>TAMANA ULTRA PRO STATUS</h1><p>Last run: $(date)</p>" > "$ROOT/index.html"
socat TCP-LISTEN:8080,fork FILE:$ROOT/index.html &

echo "[COMPLETE] $(date)" | tee -a "$LOG"
EOF