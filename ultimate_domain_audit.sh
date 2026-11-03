#!/data/data/com.termux/files/usr/bin/bash

DOMAIN="www.bd-king-r7.com"
GITHUB="tamanna456760-it.github.io"

echo "========== DOMAIN AUDIT =========="

echo "[1] Date"
date

echo "[2] Network"
ping -c 2 1.1.1.1

echo "[4] Root DNS"
dig $DOMAIN A +short

echo "[5] WWW DNS"
dig $DOMAIN A +short
dig $DOMAIN CNAME +short

echo "[6] DNSSEC"
dig $DOMAIN DNSKEY +short

echo "[7] GitHub Pages"
curl -IL --max-time 20 https://$GITHUB/Tamanna-/

echo "[8] Custom Domain HTTPS"
curl -vkI --max-time 20 https://$DOMAIN

echo "[9] Certificate"
echo | openssl s_client \
-connect $WWW:443 \
-servername $WWW 2>/dev/null \
| openssl x509 -noout -subject -issuer -dates

echo "[10] Git Status"
git status

echo "[11] CNAME"
cat CNAME 2>/dev/null

echo "========== FINISHED =========="
