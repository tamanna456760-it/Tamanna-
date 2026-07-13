#!/bin/sh
# ==================================================
# Tamanna Ultra Defense System (Level 3)
# Defensive • Anti-Backdoor • Self-Healing
# ==================================================

BASE="/root/.tamanna_guard"
LOG="$BASE/guard.log"
SAFE_USERS="root"

mkdir -p "$BASE"
echo "=== Defense Start: $(date) ===" >> "$LOG"

# --------------------------------------------------
# 1. Kill known malicious tools & miners
# --------------------------------------------------
BAD_PROC="xmrig minerd kinsing bashirc kdevtmpfsi python.perl wget curl nc ncat socat"

for p in $BAD_PROC; do
    pkill -9 -f "$p" 2>/dev/null && echo "[KILL] $p" >> "$LOG"
done

# --------------------------------------------------
# 2. Deep cron purge (persistence killer)
# --------------------------------------------------
for c in /etc/cron*/* /var/spool/cron/*; do
    [ -f "$c" ] || continue
    grep -E "curl|wget|bash|sh|nc|python|perl" "$c" >/dev/null 2>&1 && {
        cp "$c" "$c.bak"
        sed -i '/curl\|wget\|bash\|sh\|nc\|python\|perl/d' "$c"
        echo "[CRON CLEAN] $c" >> "$LOG"
    }
done

# --------------------------------------------------
# 3. Remove all SSH backdoors
# --------------------------------------------------
for h in /root /home/*; do
    AK="$h/.ssh/authorized_keys"
    [ -f "$AK" ] && {
        cp "$AK" "$AK.bak"
        > "$AK"
        chmod 600 "$AK"
        echo "[SSH CLEAN] $AK" >> "$LOG"
    }
done

# --------------------------------------------------
# 4. Lock SSH configuration (key brute defense)
# --------------------------------------------------
SSHD="/etc/ssh/sshd_config"
if [ -f "$SSHD" ]; then
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' "$SSHD"
    sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' "$SSHD"
    systemctl restart sshd 2>/dev/null
    echo "[SSH HARDENED]" >> "$LOG"
fi

# --------------------------------------------------
# 5. Remove ALL non-root users (hard mode)
# --------------------------------------------------
for u in $(cut -d: -f1 /etc/passwd); do
    echo "$SAFE_USERS" | grep -qw "$u" && continue
    userdel -r "$u" 2>/dev/null && echo "[USER REMOVED] $u" >> "$LOG"
done

# --------------------------------------------------
# 6. Firewall lockdown (only SSH allowed)
# --------------------------------------------------
if command -v iptables >/dev/null 2>&1; then
    iptables -F
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    echo "[FIREWALL LOCKED]" >> "$LOG"
fi

# --------------------------------------------------
# 7. File immutability (self-heal)
# --------------------------------------------------
chattr +i /etc/passwd /etc/shadow /etc/group /etc/ssh/sshd_config 2>/dev/null
echo "[IMMUTABLE SET]" >> "$LOG"

# --------------------------------------------------
# 8. Kernel hardening
# --------------------------------------------------
sysctl -w net.ipv4.tcp_syncookies=1
sysctl -w net.ipv4.conf.all.accept_redirects=0
sysctl -w net.ipv4.conf.all.send_redirects=0
sysctl -w kernel.randomize_va_space=2
echo "[KERNEL HARDENED]" >> "$LOG"

# --------------------------------------------------
# 9. Self-defense auto-start
# --------------------------------------------------
(crontab -l 2>/dev/null; echo "@reboot $BASE/tamanna_ultra_defense.sh") | crontab -

echo "=== SYSTEM FULLY LOCKED ===" >> "$LOG"