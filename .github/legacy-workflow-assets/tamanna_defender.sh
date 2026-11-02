#!/bin/sh

# ==============================
# Tamanna Defensive System v1.0
# Author: tamanna456760@gmail.com
# ==============================

BASE_DIR="/root/tamanna_security"
LOG="$BASE_DIR/defender.log"
WHITELIST="$BASE_DIR/whitelist.txt"

mkdir -p "$BASE_DIR"

echo "[+] Defender started at $(date)" >> "$LOG"

# ------------------------------
# 1. Allow only original system
# ------------------------------
HOST_ID="$(cat /etc/machine-id 2>/dev/null)"

if [ ! -f "$WHITELIST" ]; then
    echo "$HOST_ID" > "$WHITELIST"
    echo "[+] Original system registered" >> "$LOG"
fi

if ! grep -q "$HOST_ID" "$WHITELIST"; then
    echo "[!] Unauthorized system detected" >> "$LOG"
    echo "[!] Blocking system..." >> "$LOG"
    shutdown -h now
fi

# ------------------------------
# 2. Disable dangerous services
# ------------------------------
for svc in telnet ftp rsh; do
    if command -v systemctl >/dev/null 2>&1; then
        systemctl stop "$svc" 2>/dev/null
        systemctl disable "$svc" 2>/dev/null
    fi
done

# ------------------------------
# 3. Firewall basic protection
# ------------------------------
if command -v iptables >/dev/null 2>&1; then
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT

    iptables -A INPUT -i lo -j ACCEPT
    iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
fi

# ------------------------------
# 4. Auto remove unknown users
# ------------------------------
for u in $(cut -d: -f1 /etc/passwd); do
    case "$u" in
        root|daemon|bin|sys|sync|games|man|lp|mail|news|uucp|proxy|www-data|backup|list|irc|gnats|nobody)
            ;;
        *)
            if [ "$u" != "$(whoami)" ]; then
                userdel -r "$u" 2>/dev/null
                echo "[!] Removed unknown user: $u" >> "$LOG"
            fi
            ;;
    esac
done

# ------------------------------
# 5. Defender always active
# ------------------------------
(crontab -l 2>/dev/null; echo "@reboot $BASE_DIR/tamanna_defender.sh") | crontab -

echo "[✓] System secured successfully" >> "$LOG"