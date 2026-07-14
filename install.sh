#!/usr/bin/env bash

set -e

echo "======================================"
echo "🚀 Tamanna System Installer"
echo "======================================"

# Check Python
if command -v python3 >/dev/null 2>&1; then
    echo "✅ Python: $(python3 --version)"
else
    echo "❌ Python3 not found."
    exit 1
fi

# Check pip
if command -v pip3 >/dev/null 2>&1; then
    echo "✅ pip3 found"

    if [ -f requirements.txt ]; then
        echo "📦 Installing Python packages..."
        pip3 install -r requirements.txt
    else
        echo "⚠️ requirements.txt not found."
    fi
fi

# Check Node.js
if command -v node >/dev/null 2>&1; then
    echo "✅ Node.js: $(node --version)"

    if [ -f package.json ]; then
        echo "📦 Installing Node packages..."
        npm install
    else
        echo "⚠️ package.json not found."
    fi
fi

# Create project directories
mkdir -p logs
mkdir -p reports
mkdir -p data
mkdir -p backups

echo "📁 Project directories created."

# Make scripts executable
find . -maxdepth 1 -name "*.sh" -exec chmod +x {} \;

echo "======================================"
echo "✅ Installation Complete"
echo "======================================"
