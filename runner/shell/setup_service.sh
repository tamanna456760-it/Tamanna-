#!/usr/bin/env bash
set -euo pipefail

# Run as root (sudo)
# Create user
USERNAME="myauto"
if ! id -u "$USERNAME" >/dev/null 2>&1; then
  useradd -r -m -d /home/${USERNAME} -s /usr/sbin/nologin ${USERNAME}
fi

# Create directories
mkdir -p /opt/myauto
chown -R ${USERNAME}:${USERNAME} /opt/myauto

# Copy app files (assume deploy copies files into /opt/myauto)
# Example: you will scp or git clone into /opt/myauto before running this script.

# Create log file
touch /var/log/myauto.log
chown ${USERNAME}:${USERNAME} /var/log/myauto.log
chmod 640 /var/log/myauto.log

# Config dir
mkdir -p /etc/myauto
chown ${USERNAME}:${USERNAME} /etc/myauto
chmod 750 /etc/myauto

# Create systemd service
cat > /etc/systemd/system/myauto.service <<'EOF'
[Unit]
Description=My Auto Full-Power Worker
After=network.target

[Service]
Type=simple
User=myauto
Group=myauto
WorkingDirectory=/opt/myauto
ExecStart=/usr/bin/env python3 /opt/myauto/app/main.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable
systemctl daemon-reload
systemctl enable myauto.service
systemctl restart myauto.service

echo "Setup complete. Service status:"
systemctl --no-pager status myauto.service