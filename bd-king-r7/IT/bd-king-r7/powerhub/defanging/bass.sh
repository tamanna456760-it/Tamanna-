# basic firewall - allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp         # SSH (consider changing port)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades

# create a non-root user and disable root SSH login
sudo adduser deployer
sudo usermod -aG sudo deployer
# in /etc/ssh/sshd_config: PermitRootLogin no, PasswordAuthentication no (use keys)
sudo systemctl restart sshd