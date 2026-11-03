"""PowerHub safety controller.

Automatic file rewriting, arbitrary .bad script execution, dependency installation,
and git add/commit/push are disabled. This module only audits a project tree.
"""
from pathlib import Path
import json
import os

ROOT = Path(os.getenv("TAMANNA_POWERHUB_ROOT", "bd-king-r7/it")).resolve()
EXCLUDED = {".git", ".venv", "venv", "node_modules", "__pycache__"}


def audit_files():
    findings = []
    if not ROOT.is_dir():
        return {"status": "unavailable", "reason": "project root does not exist", "findings": []}
    for current, dirs, files in os.walk(ROOT):
        dirs[:] = [name for name in dirs if name not in EXCLUDED]
        for name in files:
            path = Path(current) / name
            try:
                if path.stat().st_size == 0:
                    findings.append({"path": str(path.relative_to(ROOT)), "finding": "empty_file", "action": "manual_review"})
                elif path.suffix == ".bad":
                    findings.append({"path": str(path.relative_to(ROOT)), "finding": "executable_script_requires_review", "action": "manual_review"})
            except OSError:
                findings.append({"path": str(path), "finding": "stat_failed", "action": "manual_review"})
    return {"status": "completed", "files_requiring_review": len(findings), "findings": findings, "automatic_repair": False, "automatic_script_execution": False, "automatic_git_sync": False}


def powerhub_master():
    return audit_files()


if __name__ == "__main__":
    print(json.dumps(powerhub_master(), ensure_ascii=False, indent=2))
