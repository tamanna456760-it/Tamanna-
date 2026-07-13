#!/usr/bin/env python3
import json
import shutil
import re
from pathlib import Path
from datetime import datetime

FILE = Path("package.json")

if not FILE.exists():
    print("❌ package.json not found")
    exit(1)

# Backup
backup = FILE.with_suffix(
    f".backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
)

shutil.copy(FILE, backup)
print(f"✅ Backup created: {backup}")

data = FILE.read_text(errors="ignore")

# Try normal JSON parse
try:
    json.loads(data)
    print("✅ package.json already valid")
    exit(0)

except json.JSONDecodeError as e:
    print("⚠️ JSON error detected")
    print(e)

# Detect multiple JSON objects
parts = re.split(r'\n\s*\}\s*\n\s*\{', data)

if len(parts) > 1:
    print("⚠️ Multiple JSON blocks detected")

    fixed = parts[0] + "\n}"

    try:
        obj = json.loads(fixed)

        FILE.write_text(
            json.dumps(obj, indent=2) + "\n"
        )

        print("✅ Auto repaired first JSON block")
        print("Run: npm install")

    except Exception:
        print("❌ Auto repair failed")
        print("Manual repair required")

else:
    print("❌ Unknown JSON corruption")
    print("Use: cat -n package.json")
