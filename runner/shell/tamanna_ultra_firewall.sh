cat > ~tamanna_ultra_firewall.sh << 'EOF'
#!/bin/sh
# =========================================
# TAMANNA ULTRA SYSTEM + AUTO FIREWALL
# BD-KING-R7 + Auto Code + Comm + Unlimited Firewall
# =========================================

ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/ultra_firewall.log"
mkdir -p "$ROOT/logs"

echo "=== ULTRA FIREWALL SYSTEM START ===" > "$LOG"
cd "$ROOT" || exit

# 1️⃣ Install dependencies
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip curl wget iptables 2>>"$LOG"

# 2️⃣ Harden system (permissions)
echo "[SEC] Setting strict permissions" | tee -a "$LOG"
find . -type d -exec chmod 700 {} \;
find . -type f -exec chmod 600 {} \;

# 3️⃣ Auto generate Python secure code
GEN_PY="$ROOT/python/secure_auto_$(date +%s).py"
mkdir -p "$ROOT/python"
echo "import secrets, hashlib; print('Secure Token:', hashlib.sha256(secrets.token_bytes(32)).hexdigest())" > "$GEN_PY"
echo "[AUTO GEN] Python secure code generated: $GEN_PY" | tee -a "$LOG"

# 4️⃣ Run all code (Python/Node/Shell/C/Java)
for TYPE in python node shell c_programs java_programs; do
    for f in $(find "./$TYPE" -type f 2>/dev/null); do
        echo "[RUN] $f" | tee -a "$LOG"
        case $TYPE in
            python) python3 "$f" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
            node) node "$f" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
            shell) sh "$f" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
            c_programs)
                OUT="${f%.c}.out"
                gcc "$f" -o "$OUT" && "$OUT" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
            java_programs)
                cls=$(basename "$f" .java)
                javac "$f" -d ./java_programs 2>>"$LOG" && java -cp ./java_programs "$cls" >>"$LOG" 2>&1 || echo "[ERROR] $f" | tee -a "$LOG";;
        esac
    done
done

# 5️⃣ Auto firewall unlimited rules
echo "[FIREWALL] Generating unlimited firewall rules" | tee -a "$LOG"
# Flush previous rules
iptables -F
iptables -X
# Default deny all incoming, allow outgoing
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT
# Allow local loopback
iptables -A INPUT -i lo -j ACCEPT
# Allow SSH (port 22)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
# Example dynamic rules: block suspicious IPs
for ip in $(cat "$ROOT/attack_ips.txt" 2>/dev/null); do
    iptables -A INPUT -s $ip -j DROP
done
# Save rules
iptables-save > "$ROOT/logs/firewall_rules_$(date +%Y%m%d%H%M%S).txt"
echo "[FIREWALL] Rules saved" | tee -a "$LOG"

# 6️⃣ Auto backup zip
for d in $(find . -type d -name "backup"); do
    ZIPFILE="$ROOT/zip_backups/$(basename $d)-$(date +%Y%m%d%H%M%S).zip"
    mkdir -p "$ROOT/zip_backups"
    zip -r "$ZIPFILE" "$d" >>"$LOG" 2>&1
done

# 7️⃣ GitHub auto push securely
git add .
git commit -m "ULTRA FIREWALL AUTO $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit" | tee -a "$LOG"
read -p "GitHub Username: " USER
read -sp "GitHub Token: " TOKEN
echo
git remote remove origin 2>/dev/null
git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
git push -u origin main >>"$LOG" 2>&1 || echo "GitHub Push failed" | tee -a "$LOG"

# 8️⃣ Heartbeat / communication
echo "[COMM] Heartbeat: $(date) | Firewall active, system secure" | tee -a "$LOG"

echo "=== ULTRA FIREWALL SYSTEM COMPLETE ===" | tee -a "$LOG"
echo "Check log: $LOG"
EOF