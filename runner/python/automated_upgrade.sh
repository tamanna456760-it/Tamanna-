#!/usr/bin/env bash
set -Eeuo pipefail

echo "Nmap Upgrade Validation Script"
echo "==============================="

if ! command -v nmap >/dev/null 2>&1; then
  echo "Nmap is not installed; install it before running this validation." >&2
  exit 1
fi

echo "Current Nmap version:"
nmap --version | head -n 2

if [[ -f "nmap_test_suite.py" ]]; then
  echo "Running comprehensive Python test suite..."
  python3 nmap_test_suite.py
else
  echo "SKIP: nmap_test_suite.py was not found."
fi

echo "Validating Nmap script database..."
nmap --script-updatedb
echo "Upgrade test sequence finished."
