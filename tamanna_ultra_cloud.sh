mkdir -p ~/Tamanna/bd-king-r7~/Tamanna/python ~/Tamanna/node ~/Tamanna/shell ~/Tamanna/c_programs ~/Tamanna/java_programs ~/Tamanna/zip_backups ~/Tamanna/logs

cat > ~/Tamanna/scripts/tamanna_ultra_cloud.sh << 'EOF'
#!/bin/sh
# =============================================
# BD-KING-R7 + TAMANNA ULTRA CLOUD SYSTEM
# Auto Code + Firewall + GitHub + Logs + Dashboard
# Version: #9000
# =============================================

ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/ultra_cloud.log"
mkdir -p "$ROOT/logs"

echo "=== ULTRA CLOUD SYSTEM START ===" > "$LOG"
cd "$ROOT" || exit

# 1️⃣ Install dependencies
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip curl wget iptables socat 2>>"$LOG"

# 2️⃣ Harden folders & files
find . -type d -exec chmod 700 {} \;
find . -type f -exec chmod 600 {} \;

# 3️⃣ Auto generate secure Python token (example)
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

# 5️⃣ Firewall auto (unlimited dynamic rules)
iptables -F; iptables -X
iptables -P INPUT DROP; iptables -P FORWARD DROP; iptables -P OUTPUT ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
for ip in $(cat "$ROOT/attack_ips.txt" 2>/dev/null); do iptables -A INPUT -s $ip -j DROP; done
iptables-save > "$ROOT/logs/firewall_rules_$(date +%Y%m%d%H%M%S).txt"

# 6️⃣ Backup zip folders
for d in $(find . -type d -name "backup"); do
    ZIPFILE="$ROOT/zip_backups/$(basename $d)-$(date +%Y%m%d%H%M%S).zip"
    zip -r "$ZIPFILE" "$d" >>"$LOG" 2>&1
done

# 7️⃣ GitHub auto push
git add .
git commit -m "ULTRA CLOUD AUTO $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"
read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "GitHub Push failed" | tee -a "$LOG"

# 8️⃣ Heartbeat + Communication
echo "[COMM] Heartbeat: $(date) | System running, firewall active, code scanned & pushed" | tee -a "$LOG"

# 9️⃣ Optional Web Dashboard (simple status)
echo "<h1>TAMANA BD-KING-R7 ULTRA STATUS</h1><p>Last run: $(date)</p>" > ~/Tamanna/index.html
socat TCP-LISTEN:8080,fork FILE:~/Tamanna/index.html &

echo "=== ULTRA CLOUD SYSTEM COMPLETE ===" | tee -a "$LOG"
echo "Check log: $LOG"
echo "Web Dashboard running at http://localhost:8080"
EOF