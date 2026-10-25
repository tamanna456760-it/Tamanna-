#!/usr/bin/env python3
"""Tamanna AI: build a repair plan without modifying source files.

Owner: HM INSAN ALI
"""

from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / ".tamanna-review" / "python-audit.txt"
OUTPUT = ROOT / ".tamanna-review" / "repair-plan.json"

# Review core application modules before optional tools.
PRIORITY = {
    "main.py": 1,
    "Main.py": 1,
    "tamanna_ai.py": 2,
    "tamanna_deep_power.py": 3,
    "radar.py": 4,
    "signal.py": 4,
}

def priority_for(path: str) -> int:
    return PRIORITY.get(Path(path).name, 10)

def main() -> int:
    if not AUDIT.exists():
        print(f"Audit report not found: {AUDIT}")
        print("Run scripts/tamanna_python_audit.py first.")
        return 1

    content = AUDIT.read_text(encoding="utf-8")
    failures = []
    current = None
    details = []

    for line in content.splitlines():
        if line.startswith("FAIL: "):
            if current:
                failures.append({
                    "file": current,
                    "details": details,
                    "priority": priority_for(current),
                    "status": "needs_manual_review",
                })
            current = line.removeprefix("FAIL: ").strip()
            details = []
        elif current and line.strip():
            details.append(line.strip())

    if current:
        failures.append({
            "file": current,
            "details": details,
            "priority": priority_for(current),
            "status": "needs_manual_review",
        })

    failures.sort(key=lambda item: (item["priority"], item["file"]))

    plan = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report": str(AUDIT.relative_to(ROOT)),
        "automatic_changes_enabled": False,
        "total_files_needing_review": len(failures),
        "items": failures,
        "safety_note": (
            "Plan only. No source files were changed. "
            "Review each file before applying a repair."
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Files needing review: {len(failures)}")
    for item in failures:
        print(
            f"[Priority {item['priority']}] "
            f"{item['file']} — {item['status']}"
        )

    print(f"\nRepair plan saved: {OUTPUT.relative_to(ROOT)}")
    print("No source code was modified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PY

python3 -m py_compile scripts/tamanna_repair_planner.py
python3 scripts/tamanna_repair_planner.py
