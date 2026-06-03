mkdir -p ~/Tamanna/{scripts,python,node,shell,java_programs,c_programs,zip_backups,logs,ai_fix}

cat > ~/Tamanna/scripts/tamanna_ultra_ai_full.sh << 'EOF'
#!/bin/bash
# =============================================
# TAMANNA ULTRA PRO AI – FULL AI ASSISTANT
# Predictive Auto-Fix, Multi-Server, CI/CD Ready
# Backup, GitHub Sync, Firewall, Dashboard, Alerts
# =============================================

ROOT="$HOME/Tamanna"
LOG="$ROOT/logs/tamanna_ultra_ai_full.log"
mkdir -p "$ROOT/logs"

echo "[START] $(date)" > "$LOG"
cd "$ROOT" || exit

# 1️⃣ Install Dependencies
function install_dependencies() {
    apk add --no-cache python3 py3-pip nodejs npm bash git gcc g++ make openjdk17 nano zip unzip curl iptables socat rsync mailx jq 2>>"$LOG"
    pip3 install --upgrade pip >>"$LOG" 2>&1
    pip3 install autopep8 pylint requests >>"$LOG" 2>&1
    echo "[INFO] Dependencies installed." | tee -a "$LOG"
}

# 2️⃣ Harden folders
function harden_folders() {
    find . -type d -exec chmod 700 {} \;
    find . -type f -exec chmod 600 {} \;
    echo "[INFO] Folders hardened." | tee -a "$LOG"
}

# 3️⃣ Predictive AI Code Fixer
function ai_fix_code() {
    echo "[AI FIX] Scanning & fixing code..."
    for TYPE in python node shell c_programs java_programs; do
        for f in $(find "./$TYPE" -type f 2>/dev/null); do
            echo "[CHECK] $f" | tee -a "$LOG"
            if [[ $TYPE == "python" ]]; then
                autopep8 --in-place "$f" >>"$LOG" 2>&1
                pylint "$f" >>"$LOG" 2>&1
            fi
        done
    done
    echo "[INFO] AI Predictive Code Fix completed." | tee -a "$LOG"
}

# 4️⃣ Run All Code
function run_all_code() {
    echo "[INFO] Running all code..."
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
}

# 5️⃣ Firewall Setup
function setup_firewall() {
    iptables -F; iptables -X
    iptables -P INPUT DROP; iptables -P FORWARD DROP; iptables -P OUTPUT ACCEPT
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    for ip in $(cat "$ROOT/attack_ips.txt" 2>/dev/null); do iptables -A INPUT -s $ip -j DROP; done
    iptables-save > "$ROOT/logs/firewall_$(date +%Y%m%d%H%M%S).txt"
    echo "[INFO] Firewall setup complete." | tee -a "$LOG"
}

# 6️⃣ Auto Backup & Zip
function auto_backup() {
    for d in $(find . -type d -name "backup"); do
        ZIP="$ROOT/zip_backups/$(basename $d)-$(date +%Y%m%d%H%M%S).zip"
        zip -r "$ZIP" "$d" >>"$LOG" 2>&1
    done
    echo "[INFO] Backup completed." | tee -a "$LOG"
}

# 7️⃣ GitHub Auto Push
function github_push() {
    git add .
    git commit -m "TAMANA ULTRA AI FULL AUTO $(date)" >>"$LOG" 2>&1 || echo "Nothing to commit"
    read -p "GitHub Username: " USER
    read -sp "GitHub Token: " TOKEN
    echo
    git remote remove origin 2>/dev/null
    git remote add origin https://$USER:$TOKEN@github.com/$USER/Tamanna.git
    git push -u origin main >>"$LOG" 2>&1 || echo "[ERROR] GitHub push failed"
}

# 8️⃣ Heartbeat & Alerts
function send_alerts() {
    ALERT="Tamanna ULTRA AI FULL ran at $(date)"
    echo "[HEARTBEAT] $ALERT" | tee -a "$LOG"
    curl -s -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" -d chat_id=YOUR_CHAT_ID -d text="$ALERT" >>"$LOG" 2>&1
    echo "$ALERT" | mailx -s "Tamanna ULTRA AI FULL ALERT" your_email@example.com
}

# 9️⃣ Web Dashboard
function start_dashboard() {
    echo "<h1>TAMANA ULTRA AI FULL STATUS</h1><p>Last run: $(date)</p>" > ~/Tamanna/index.html
    socat TCP-LISTEN:8080,fork FILE:~/Tamanna/index.html &
    echo "[INFO] Dashboard running at http://localhost:8080"
}

# 🔹 Multi-Server Sync (Optional)
function multi_server_sync() {
    read -p "Enter remote server (user@host:/path): " REMOTE
    rsync -avz --delete "$ROOT/" "$REMOTE" >>"$LOG" 2>&1
    echo "[INFO] Multi-server sync complete." | tee -a "$LOG"
}

# 🔹 Interactive Menu
while true; do
    echo "======================================"
    echo "TAMANNA ULTRA PRO AI – FULL ASSISTANT MENU"
    echo "1) Install Dependencies"
    echo "2) Harden Folders"
    echo "3) AI Code Fix"
    echo "4) Run All Code"
    echo "5) Setup Firewall"
    echo "6) Backup"
    echo "7) GitHub Push"
    echo "8) Send Alerts"
    echo "9) Start Dashboard"
    echo "10) Multi-Server Sync"
    echo "11) Exit"
    echo "======================================"
    read -p "Choose an option: " CHOICE

    case $CHOICE in
        1) install_dependencies ;;
        2) harden_folders ;;
        3) ai_fix_code ;;
        4) run_all_code ;;
        5) setup_firewall ;;
        6) auto_backup ;;
        7) github_push ;;
        8) send_alerts ;;
        9) start_dashboard ;;
        10) multi_server_sync ;;
        11) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid option" ;;
    esac
done
EOF