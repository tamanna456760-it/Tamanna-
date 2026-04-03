cat > tamanna_repair.sh << 'EOF'
#!/bin/sh

echo "=== TAMANNA AUTO REPAIR SYSTEM ==="

DIR="$HOME/Tamanna"
cd "$DIR" || { echo "Folder not found"; exit 1; }

echo "[1] Fix permissions"
find . -type f -name "*.sh" -exec chmod +x {} \;

echo "[2] Remove Windows line endings"
find . -type f -exec sed -i 's/\r$//' {} \;

echo "[3] Python syntax check"
for f in $(find . -name "*.py"); do
    echo "Checking $f"
    python3 -m py_compile "$f" 2>/dev/null || echo "ERROR in $f"
done

echo "[4] NodeJS check"
for f in $(find . -name "*.js"); do
    node "$f" >/dev/null 2>&1 || echo "JS issue in $f"
done

echo "[5] Shell script test"
for f in $(find . -name "*.sh"); do
    sh -n "$f" || echo "Shell error in $f"
done

echo "[6] Install dependencies"
[ -f requirements.txt ] && pip3 install -r requirements.txt
[ -f package.json ] && npm install

echo "[7] Run main files"
[ -f main.py ] && python3 main.py
[ -f app.py ] && python3 app.py
[ -f index.js ] && node index.js
[ -f main.sh ] && sh main.sh

echo "[8] Git save"
git add .
git commit -m "Auto repair backup $(date)"

echo "=== REPAIR COMPLETE ==="
EOF