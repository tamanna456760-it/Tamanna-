#!/bin/bash

echo "🔍 Detecting project type..."
sleep 1

# -----------------------------
# 1) NODE PROJECT DETECT
# -----------------------------
if [ -f "package.json" ]; then
    echo "📦 Node.js project detected"
    if command -v npm >/dev/null 2>&1; then
        echo "➡️ Running: npm install"
        npm install
    else
        echo "❌ npm not installed"
    fi
fi

# -----------------------------
# 2) PYTHON PROJECT DETECT
# -----------------------------
if [ -f "requirements.txt" ]; then
    echo "🐍 Python project detected"
    if command -v pip3 >/dev/null 2>&1; then
        echo "➡️ Running: pip3 install -r requirements.txt"
        pip3 install -r requirements.txt
    else
        echo "❌ pip3 not installed"
    fi
fi

# -----------------------------
# 3) JAVA / MAVEN PROJECT DETECT
# -----------------------------
if [ -f "pom.xml" ]; then
    echo "☕ Maven/Java project detected"
    if command -v mvn >/dev/null 2>&1; then
        echo "➡️ Running: mvn install"
        mvn install
    else
        echo "❌ Maven not installed"
    fi
fi

# -----------------------------
# 4) SHELL SCRIPTS AUTO‑ENABLE
# -----------------------------
echo "🔧 Making all .sh files executable..."
chmod +x *.sh 2>/dev/null

# -----------------------------
# 5) AUTO‑RUN MAIN FILE
# -----------------------------
echo "🚀 Checking for runnable entry files..."

if [ -f "start.sh" ]; then
    echo "➡️ Running start.sh"
    bash start.sh
    exit
fi

if [ -f "main.py" ]; then
    echo "➡️ Running python3 main.py"
    python3 main.py
    exit
fi

if [ -f "index.js" ]; then
    echo "➡️ Running node index.js"
    node index.js
    exit
fi

echo "✔ Installation complete."
echo "⚠️ No auto‑run file found."
