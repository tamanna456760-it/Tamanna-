mkdir -p ~/Tamanna/{scripts,python,node,shell,java_programs,c_programs,zip_backups,logs}

cat > ~/Tamanna/scripts/tamanna_success_program.sh << 'EOF'
#!/bin/sh
# =============================================
# TAMANNA ULTRA PRO SUCCESS PROGRAM
# Interactive, Auto-run, Auto-fix, GitHub, Backup, Firewall, Alerts
# =============================================

ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/tamanna_success.log"
mkdir -p "$ROOT/logs"

echo "[START] $(date)" > "$LOG"
cd "$ROOT" || exit

# 1️⃣ Dependencies install
apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip curl iptables socat rsync mailx jq 2>>"$LOG"

# 2️⃣ Harden folders
find . -type d -exec chmod 700 {} \;
find . -type f -exec chmod 600 {} \;

# 3️⃣ Interactive CLI Menu
echo "Welcome to TAMANNA ULTRA PRO SUCCESS PROGRAM"
echo "1) Run All Code"
echo "2) Auto Backup & Zip"
echo "3) Setup Firewall"
echo "4) GitHub Push"
echo "5) Web Dashboard"
echo "6) Exit"
read -p "Choose an option: " CHOICE

case $CHOICE in
1)
    # Run all code
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
    ;;
2)
    # Backup
    for d in $(find . -type d -name "backup"); do
        ZIP="$ROOT/zip_backups/$(basename $d)-$(date +%Y%m%d%H%M%S).zip"
        zip -r "$ZIP" "$d" >>"$LOG" 2>&1
    done
    ;;
3)
    # Firewall
    iptables -F; iptables -X
    iptables -P INPUT DROP; iptables -P FORWARD DROP; iptables -P OUTPUT ACCEPT
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    for ip in $(cat "$ROOT/attack_ips.txt" 2>/dev/null); do iptables -A INPUT -s $ip -j DROP; done
    iptables-save > "$ROOT/logs/firewall_$(date +%Y%m%d%H%M%S).txt"
    ;;
4)
    # GitHub Push
    git add .
    git commit -m "TAMANA SUCCESS AUTO $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit"
    read -p "GitHub Username: " USER
    read -sp "GitHub Token: " TOKEN
    echo
    git remote remove origin 2>/dev/null
    git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
    git push -u origin main >>"$LOG" 2>&1 || echo "[ERROR] GitHub push failed"
    ;;
5)
    # Web Dashboard
    echo "<h1>TAMANA SUCCESS PROGRAM STATUS</h1><p>Last run: $(date)</p>" > ~/Tamanna/index.html
    socat TCP-LISTEN:8080,fork FILE:~/Tamanna/index.html &
    echo "Dashboard running at http://localhost:8080"
    ;;
6)
    echo "Exiting..."
    exit 0
    ;;
*)
    echo "Invalid option"
    ;;
esac

# 6️⃣ Alerts (Telegram + Email)
ALERT="Tamanna ULTRA SUCCESS PROGRAM ran at $(date)"
curl -s -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" -d chat_id=YOUR_CHAT_ID -d text="$ALERT" >>"$LOG" 2>&1
echo "$ALERT" | mailx -s "Tamanna SUCCESS ALERT" your_email@example.com

echo "[COMPLETE] $(date)" | tee -a "$LOG"
EOF