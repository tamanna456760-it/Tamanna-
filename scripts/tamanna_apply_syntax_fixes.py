
#!/usr/bin/env python3
"""Apply narrowly scoped syntax repairs with backups; never push to GitHub."""

from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
BACKUP = ROOT / ".tamanna-repair-backup" / datetime.now(
    timezone.utc
).strftime("%Y%m%d_%H%M%S")


def replace_once(path, old, new):
    file_path = ROOT / path
    if not file_path.is_file():
        print(f"SKIP missing file: {path}")
        return False

    source = file_path.read_text(encoding="utf-8")
    count = source.count(old)

    if count != 1:
        print(f"STOP {path}: expected one exact match, found {count}")
        return False

    backup_path = BACKUP / path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file_path, backup_path)

    updated = source.replace(old, new, 1)
    file_path.write_text(updated, encoding="utf-8")
    print(f"PATCHED: {path}")
    return True


def main():
    if not (ROOT / ".git").exists():
        print("STOP: Run this from a Git repository checkout.")
        return 2

    patches = [
        (
            "runner/python/ai_file_serial_manager.py",
            '                f"{prefix}_{?}"  # placeholder, actual new name unknown yet',
            '                ""  # target filename is not known at this stage',
        ),
        (
            "runner/python/bd-king-r7_ai.py",
            "    def __init__(self, data=tamanna456760-it):",
            "    def __init__(self, data=None):",
        ),
        (
            "runner/python/bd-king-r7_ai.py",
            "warnings.filterwarnings('warking')",
            "warnings.filterwarnings('warning')",
        ),
        (
            "runner/python/bd-king-r7_ai.py",
            """            insights.append(f"🔗 Strong correlation between {high_corr['""",
            """            variables = high_corr.get("variables", [])
            if len(variables) >= 2:
                insights.append(
                    f"🔗 Strong correlation between {variables[0]} "
                    f"and {variables[1]} "
                    f"(correlation: {high_corr.get('correlation', 'unknown')})"
                )""",
        ),
        (
            "runner/python/auto_code_manager.py",
            'subprocess.run(["git", "config", "--global", "user.name", tamanna456760-it])',
            'subprocess.run(["git", "config", "--global", "user.name", name], check=True)',
        ),
        (
            "runner/python/auto_code_manager.py",
            'subprocess.run(["git", "config", "--global", "user.email", tamanna456760@gmail.com])',
            'subprocess.run(["git", "config", "--global", "user.email", email], check=True)',
        ),
        (
            "runner/python/auto_code_manager.py",
            'self.github_url = f"https://github.com/{tamanna456760-it}/{tamanna-}.git"',
            'self.github_url = f"https://github.com/{name}/{repo_name}.git"',
        ),
        (
            "runner/python/tamanna_update.py",
            "\nTamanna AI - Complete Interactive Kali Linux Manager\nWith Real-time Command Processing\n\n\nclass TamannaAI:",
            '\n"""Tamanna AI - Complete Interactive Kali Linux Manager.\nWith real-time command processing.\n"""\n\nclass TamannaAI:',
        ),
    ]

    failed = False
    for path, old, new in patches:
        if not replace_once(path, old, new):
            failed = True

    # Preserve the original configuration block as comments instead of
    # deleting it or pretending it is executable Python.
    core = ROOT / "runner/python/tamanna_core.py"
    if core.is_file():
        source = core.read_text(encoding="utf-8")
        header = (
            "[NET-AI]\n"
            "    ai-distribution: global\n"
            "    ai-sync: 100%\n"
            "    ai-focus: precision + expansion\n"
            "    ai-memory: active\n"
            "    ai-echo: continuous\n"
            "    ai-identity: TAMANNA-SYSTEM\n"
            "    ai-powerhub-link: BD-KING-R7\n"
        )
        if source.startswith(header):
            backup_path = BACKUP / "runner/python/tamanna_core.py"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(core, backup_path)
            commented = "".join("# " + line for line in header.splitlines(True))
            core.write_text(commented + source[len(header):], encoding="utf-8")
            print("PATCHED: runner/python/tamanna_core.py")
        elif not source.startswith("# [NET-AI]"):
            print("STOP runner/python/tamanna_core.py: header did not match")
            failed = True
        else:
            print("SKIP already commented: runner/python/tamanna_core.py")
    else:
        print("SKIP missing file: runner/python/tamanna_core.py")

    if BACKUP.exists():
        print(f"Backups: {BACKUP.relative_to(ROOT)}")

    print("No Git commit or push was performed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
