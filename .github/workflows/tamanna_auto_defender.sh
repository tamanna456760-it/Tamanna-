#!/bin/sh
# ===============================
# Tamanna Auto Defense System
# Defensive • Legal • Safe
# ===============================

BASE="/root/tamanna_defense"
LOG="$BASE/defense.log"

mkdir -p "$BASE"
echo "[+] Defense start: $(date)" >> "$LOG"

# ---------------------------------
# 1. Kill suspicious processes
# ---------------------------------
for p in xmrig minerd kinsing cryptominer; do
    pkill -f "$p" 2>/dev/null && echo "[!] Killed process: $p" >> "$LOG"
done

# ---------------------------------
# 2. Remove suspicious cron jobs
# ---------------------------------
for f in /var/spool/cron/* /etc/cron*/*; do
    if grep -E "curl|wget|bash|sh|nc|python" "$f" 2>/dev/null; then
        cp "$f" "$f.bak"
        sed -i '/curl\|wget\|bash\|sh\|nc\|python/d' "$f"
        echo "[!] Cleaned cron: $f" >> "$LOG"
    fi
done

# ---------------------------------
# 3. Remove unknown SSH keys
# ---------------------------------
for home in /home/* /root; do
    AUTH="$home/.ssh/authorized_keys"
    if [ -f "$AUTH" ]; then
        cp "$AUTH" "$AUTH.bak"
        sed -i '/ssh-rsa\|ssh-ed25519/d' "$AUTH"
        echo "[!] SSH keys removed from $home" >> "$LOG"
    fi
done

# ---------------------------------
# 4. Disable dangerous services
# ---------------------------------
for svc in telnet ftp rsh rpcbind; do
    systemctl stop "$svc" 2>/dev/null
    systemctl disable "$svc" 2>/dev/null
done

# ---------------------------------
# 5. Lock SSH brute-force
# ---------------------------------
if command -v iptables >/dev/null 2>&1; then
    iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
    iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
fi

# ---------------------------------
# 6. Remove unknown users
# ---------------------------------
for u in $(cut -d: -f1 /etc/passwd); do
    case "$u" in
        root|daemon|bin|sys|sync|games|man|lp|mail|news|uucp|proxy|www-data|backup|list|irc|gnats|nobody)
            ;;
        *)
            userdel -r "$u" 2>/dev/null && echo "[!] Removed user: $u" >> "$LOG"
            ;;
    esac
done

# ---------------------------------
# 7. Protect important files
# ---------------------------------
chattr +i /etc/passwd /etc/shadow /etc/group 2>/dev/null

# ---------------------------------
# 8. Auto-run on boot (always active)
# ---------------------------------
(crontab -l 2>/dev/null; echo "@reboot $BASE/tamanna_auto_defense.sh") | crontab -

echo "[✓] System cleaned & protected" >> "$LOG"