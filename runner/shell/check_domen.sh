#!/bin/bash

DOMAIN="bd-king-r7.com"

echo "=============================================="
echo "   BD-KING-R7 DOMAIN DIAGNOSTIC"
echo "   Checking: $DOMAIN"
echo "=============================================="

echo ""
echo "🔍 Checking DNS resolution..."
if nslookup "$DOMAIN" >/dev/null 2>&1; then
    echo "✅ DNS found an IP address."
else
    echo "❌ DNS could NOT resolve the domain."
    echo "   This means:"
    echo "   - Domain is not registered, OR"
    echo "   - DNS records are missing, OR"
    echo "   - Nameservers not configured."
fi

echo ""
echo "🔍 Checking WHOIS registration..."
if command -v whois >/dev/null 2>&1; then
    whois "$DOMAIN" | head -n 20
else
    echo "⚠️ WHOIS not installed. Install with:"
    echo "   sudo apt install whois"
fi

echo ""
echo "🔍 Checking ping..."
if ping -c 1 "$DOMAIN" >/dev/null 2>&1; then
    echo "✅ Ping successful."
else
    echo "❌ Ping failed — no server reachable."
fi

echo ""
echo "✅ Diagnostic complete."
