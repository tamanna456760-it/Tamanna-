#!/usr/bin/env bash

set -e

REPORT="debug_report.txt"

echo "=========================================" > "$REPORT"
echo "Tamanna System Debug Report" >> "$REPORT"
echo "=========================================" >> "$REPORT"
echo "Generated: $(date)" >> "$REPORT"
echo "" >> "$REPORT"

echo "== System ==" >> "$REPORT"
uname -a >> "$REPORT" 2>/dev/null || true
echo "" >> "$REPORT"

echo "== Current Directory ==" >> "$REPORT"
pwd >> "$REPORT"
echo "" >> "$REPORT"

echo "== Python ==" >> "$REPORT"
python3 --version >> "$REPORT" 2>/dev/null || echo "Python3: Not Found" >> "$REPORT"
echo "" >> "$REPORT"

echo "== Node.js ==" >> "$REPORT"
node --version >> "$REPORT" 2>/dev/null || echo "Node.js: Not Found" >> "$REPORT"
echo "" >> "$REPORT"

echo "== npm ==" >> "$REPORT"
npm --version >> "$REPORT" 2>/dev/null || echo "npm: Not Found" >> "$REPORT"
echo "" >> "$REPORT"

echo "== Git ==" >> "$REPORT"
git --version >> "$REPORT" 2>/dev/null || echo "Git: Not Found" >> "$REPORT"
echo "" >> "$REPORT"

echo "== Project Files ==" >> "$REPORT"
find . -maxdepth 2 -type f | sort >> "$REPORT"
echo "" >> "$REPORT"

echo "== Disk Usage ==" >> "$REPORT"
df -h >> "$REPORT" 2>/dev/null || true
echo "" >> "$REPORT"

echo "== Memory ==" >> "$REPORT"
free -h >> "$REPORT" 2>/dev/null || echo "Memory information unavailable" >> "$REPORT"
echo "" >> "$REPORT"

echo "========================================="
echo "✅ Debug completed."
echo "📄 Report saved to: $REPORT"
echo "========================================="
