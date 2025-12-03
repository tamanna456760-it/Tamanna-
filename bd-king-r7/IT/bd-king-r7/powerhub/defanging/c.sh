# 1) enable firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 2) install fail2ban
sudo apt update && sudo apt install -y fail2ban

# 3) install security scanners for local dev
pip install bandit pip-audit safety

# 4) add HTTPS via certbot (nginx)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com