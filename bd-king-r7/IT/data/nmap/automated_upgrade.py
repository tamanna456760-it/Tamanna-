#!/bin/bash
# nmap-upgrade-test.sh - Comprehensive Nmap upgrade testing

echo "Nmap Upgrade Validation Script"
echo "==============================="

# Check current Nmap version
echo "Current Nmap version:"
nmap --version | head -n 2

# Run Python test suite
echo "Running comprehensive tests..."
python3 nmap_test_suite.py

# Test Nmap from different installation methods
echo "Testing installation methods..."
echo "1. Testing system Nmap..."
which nmap && nmap --version

echo "2. Testing compiled from source..."
if [ -f "/usr/local/bin/nmap" ]; then
    /usr/local/bin/nmap --version | head -n 1
fi

# Validate NSE script database
echo "Validating NSE script database..."
nmap --script-updatedb
echo "NSE script update completed"

echo "Upgrade test sequence finished!"