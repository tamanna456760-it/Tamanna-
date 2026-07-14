#!/data/data/com.termux/files/usr/bin/bash

echo "===== TAMANNA DOMAIN FULL DIAGNOSTIC ====="

echo "--- GitHub ---"
git remote -v
git status
git log --oneline -3

echo "--- Pages files ---"
ls -la index.html CNAME .nojekyll 2>/dev/null
echo "CNAME:"
cat CNAME 2>/dev/null


echo "--- DNS Google ---"
dig www.tamanna.com @8.8.8.8
echo "--- DNS Cloudflare ---"
dig www.tamanna.com @1.1.1.1


echo "--- HTTPS Headers ---"
curl -vkI --connect-timeout 15 https://www.tamanna.com


echo "--- GitHub Pages Origin ---"
curl -I --connect-timeout 15 https://tamanna456760-it.github.io/Tamanna-/


echo "--- SSL Certificate ---"
echo | openssl s_client \
-connect www.tamanna.com:443 \
-servername www.tamanna.com 2>/dev/null \
| openssl x509 -noout -subject -issuer -dates


echo "===== DONE ====="
