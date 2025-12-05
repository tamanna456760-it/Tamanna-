#!/bin/bash
# wireshark-test-automation.sh

echo "Wireshark Automated Testing Suite"
echo "=================================="

# Check installations
echo "1. Checking Wireshark installation..."
which wireshark && wireshark --version
which tshark && tshark --version

# Run Python test suite
echo "2. Running comprehensive tests..."
python3 wireshark_test_suite.py

# Test specific functionalities
echo "3. Testing capture interfaces..."
tshark -D

echo "4. Testing display filters..."
tshark -Y "tcp.port==80" -c 1 -a duration:5

echo "5. Testing export formats..."
tshark -T json -c 3 -a duration:5

echo "6. Testing statistics..."
tshark -z io,stat,0 -a duration:3

echo "✅ Wireshark testing completed!"