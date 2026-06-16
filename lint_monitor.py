import subprocess
import json
from datetime import datetime

TOOLS = [
    ["ruff", "check", "."],
    ["flake8", "."],
]

results = []

for tool in TOOLS:
    try:
        output = subprocess.run(
            tool,
            capture_output=True,
            text=True
        )

        results.append({
            "tool": tool[0],
            "return_code": output.returncode,
            "stdout": output.stdout,
            "stderr": output.stderr,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        results.append({
            "tool": tool[0],
            "error": str(e)
        })

with open("lint_report.json", "w") as f:
    json.dump(results, f, indent=4)

print("Lint check completed.")