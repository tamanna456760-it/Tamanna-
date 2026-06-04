#!/bin/sh
# =====================================================
# Tamanna Cyber Shield - Level 4
# Advanced Cyber Security Defense
# =====================================================

BASE="/root/.tamanna_cyber"
LOG="$BASE/cyber.log"
mkdir -p "$BASE"

echo "=== CYBER SHIELD START $(date) ===" >> "$LOG"

# -----------------------------------------------------
# 1. Install core cyber security tools
# -----------------------------------------------------
if command -v apt >/dev/null 2>&1; then
    apt update -y
    apt install -y fail2ban auditd aide lynis rkhunter
fi

# -----------------------------------------------------
# 2. Fail2Ban (bruteforce auto block)
# -----------------------------------------------------
cat > /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 1h
EOF

systemctl enable fail2ban
systemctl restart fail2ban
echo "[✓] Fail2Ban active" >> "$LOG"

# -----------------------------------------------------
# 3. Audit system calls (intrusion detect)
# -----------------------------------------------------
systemctl enable auditd
systemctl restart auditd
auditctl -e 1
echo "[✓] Auditd enabled" >> "$LOG"

# -----------------------------------------------------
# 4. File Integrity Monitor (AIDE)
# -----------------------------------------------------
aideinit
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
echo "[✓] AIDE baseline created" >> "$LOG"

# Daily integrity check
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/aide --check >> $LOG") | crontab -

# -----------------------------------------------------
# 5. Rootkit & malware scan
# -----------------------------------------------------
rkhunter --update
rkhunter --check --sk
echo "[✓] Rootkit scan done" >> "$LOG"

# -----------------------------------------------------
# 6. Kernel cyber hardening
# -----------------------------------------------------
sysctl -w kernel.kptr_restrict=2
sysctl -w kernel.dmesg_restrict=1
sysctl -w fs.protected_hardlinks=1
sysctl -w fs.protected_symlinks=1
sysctl -w net.ipv4.conf.all.rp_filter=1
sysctl -w net.ipv4.icmp_echo_ignore_broadcasts=1
echo "[✓] Kernel hardened" >> "$LOG"

# -----------------------------------------------------
# 7. Network attack protection
# -----------------------------------------------------
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP
iptables -A INPUT -m limit --limit 10/min -j ACCEPT
echo "[✓] Network shield active" >> "$LOG"

# -----------------------------------------------------
# 8. Log-based attack detection
# -----------------------------------------------------
grep -Ei "failed|invalid|attack|root login" /var/log/auth.log \
  >> "$BASE/alerts.log"

# -----------------------------------------------------
# 9. Auto start on boot
# -----------------------------------------------------
(crontab -l 2>/dev/null; echo "@reboot $BASE/tamanna_cyber_shield.sh") | crontab -

echo "=== CYBER SHIELD FULLY ACTIVE ===" >> "$LOG"