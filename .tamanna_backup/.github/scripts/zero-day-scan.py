#!/usr/bin/env python3
import csv
import re
import sys


def main():
    threat_file = None
    for i, arg in enumerate(sys.argv):
        if arg == "--threats":
            threat_file = sys.argv[i + 1]
    if not threat_file:
        print("No threat file")
        sys.exit(0)
    with open(threat_file) as f:
        threats = [row[0] for row in csv.reader(f)]
    # Get diff
    diff = subprocess.check_output(["git", "diff", "HEAD~1"], text=True)
    for threat in threats:
        if re.search(threat, diff, re.IGNORECASE):
            print(f"🚨 Zero‑day pattern detected: {threat}")
            sys.exit(1)
    print("✅ No zero‑day patterns found")
    sys.exit(0)


if __name__ == "__main__":
    import subprocess

    main()
