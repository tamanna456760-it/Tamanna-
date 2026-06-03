#!/bin/bash
# System security hardening script

echo "System Security Hardening"
echo "========================="

# Update system
sudo apt update && sudo apt upgrade -y

# Install security tools
sudo apt install -y \
    fail2ban \
    ufw \
    rkhunter \
    chkrootkit \
    lynis

# Configure firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Harden SSH
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

echo "Security hardening completed"