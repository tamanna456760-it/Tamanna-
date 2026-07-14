#!/data/data/com.termux/files/usr/bin/bash

echo "=== TAMANNA DOMAIN AUTO CHECK ==="

echo "[1] Git status"
git status

echo "[2] Remote"
git remote -v

echo "[3] CNAME"
echo "www.tamanna.com" > CNAME
cat CNAME

echo "[4] Create GitHub Pages files"
touch .nojekyll

echo "[5] Commit + Push"
git add -f CNAME .nojekyll index.html
git commit -m "Auto repair GitHub Pages domain" || true
git push origin main

echo "[6] DNS Check"
dig www.tamanna.com CNAME
dig tamanna.com A

echo "[7] GitHub Pages Check"
curl -IL https://tamanna456760-it.github.io/Tamanna-/

echo "[8] Domain HTTPS Check"
curl -vkI https://www.tamanna.com

echo "=== FINISHED ==="
