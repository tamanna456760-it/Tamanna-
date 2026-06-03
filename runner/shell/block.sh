sudo apt install fail2ban
# basic /etc/fail2ban/jail.local
cat <<'EOF' | sudo tee /etc/fail2ban/jail.local
[sshd]
enabled = true
port = ssh
filter = sshd
maxretry = 5
bantime = 600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
maxretry = 6
bantime = 600
EOF

sudo systemctl restart fail2ban