#!/bin/sh
# =========================================================
# Tamanna Cyber Fortress - LEVEL 5 (ULTRA DEFENSE)
# Legal | Defensive | Zero-Trust Architecture
# =========================================================

BASE="/root/.tamanna_fortress"
LOG="$BASE/fortress.log"
mkdir -p "$BASE"

echo "=== FORTRESS START $(date) ===" >> "$LOG"

# ---------------------------------------------------------
# 1. Install enterprise security stack
# ---------------------------------------------------------
if command -v apt >/dev/null 2>&1; then
    apt update -y
    apt install -y \
      suricata fail2ban auditd aide rkhunter lynis \
      apparmor apparmor-utils ufw
fi

# ---------------------------------------------------------
# 2. Enable IDS / IPS (Suricata)
# ---------------------------------------------------------
systemctl enable suricata
systemctl start suricata
echo "[IDS] Suricata active" >> "$LOG"

# ---------------------------------------------------------
# 3. Zero Trust Firewall (deny all by default)
# ---------------------------------------------------------
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw enable
echo "[FIREWALL] Zero Trust enforced" >> "$LOG"

# ---------------------------------------------------------
# 4. AppArmor Full Enforcement
# ---------------------------------------------------------
systemctl enable apparmor
systemctl start apparmor
aa-enforce /etc/apparmor.d/*
echo "[APPARMOR] Enforcing mode" >> "$LOG"

# ---------------------------------------------------------
# 5. Kernel Lockdown (anti rootkit)
# ---------------------------------------------------------
sysctl -w kernel.kptr_restrict=2
sysctl -w kernel.dmesg_restrict=1
sysctl -w kernel.perf_event_paranoid=3
sysctl -w kernel.yama.ptrace_scope=3
echo "[KERNEL] Locked down" >> "$LOG"

# ---------------------------------------------------------
# 6. File Integrity + Snapshot
# ---------------------------------------------------------
aideinit
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
tar czf $BASE/system_snapshot_$(date +%F).tar.gz /etc /bin /sbin
echo "[INTEGRITY] Baseline snapshot created" >> "$LOG"

# ---------------------------------------------------------
# 7. Auto isolation on intrusion
# ---------------------------------------------------------
grep -Ei "attack|malware|trojan" /var/log/suricata/fast.log && {
    ufw deny in from any
    echo "[ALERT] System isolated due to attack" >> "$LOG"
}

# ---------------------------------------------------------
# 8. Rootkit & malware sweep
# ---------------------------------------------------------
rkhunter --update
rkhunter --check --sk
echo "[SCAN] Rootkit scan done" >> "$LOG"

# ---------------------------------------------------------
# 9. Fail2Ban hard mode
# ---------------------------------------------------------
cat > /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
maxretry = 2
bantime = 24h
EOF

systemctl restart fail2ban
echo "[FAIL2BAN] Aggressive mode" >> "$LOG"

# ---------------------------------------------------------
# 10. Auto-start & self-heal
# ---------------------------------------------------------
(crontab -l 2>/dev/null; echo "@reboot $BASE/tamanna_cyber_fortress.sh") | crontab -

echo "=== FORTRESS FULLY ACTIVE ===" >> "$LOG"