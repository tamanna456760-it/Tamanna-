#!/data/data/com.termux/files/usr/bin/bash

DOMAIN="tamanna.com"
REPORT="tamanna_ai/modules/domain_monitor/domain_report.txt"

mkdir -p "$(dirname $REPORT)"

{
echo "===== TAMANNA AI DOMAIN MONITOR ====="
date

echo ""
echo "=== NAMESERVER ==="
dig NS $DOMAIN +short

echo ""
echo "=== A RECORD ==="
dig A $DOMAIN +short

echo ""
echo "=== WWW RECORD ==="
dig www.$DOMAIN A +short
dig www.$DOMAIN CNAME +short

echo ""
echo "=== HTTPS STATUS ==="
curl -I --max-time 15 https://www.$DOMAIN 2>&1

echo ""
echo "=== END ==="

} > "$REPORT"
