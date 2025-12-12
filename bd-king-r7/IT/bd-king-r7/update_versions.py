#!/usr/bin/env python3
"""Update selected files to the central VERSION value."""
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
# repo root (bd-king-r7)
REPO_ROOT = ROOT.parents[1]
VFILE = ROOT / "VERSION"
if not VFILE.exists():
    raise SystemExit("VERSION file not found")

VERSION = VFILE.read_text().strip()

REPLACEMENTS = [
    # (file, pattern, replacement_template)
    (REPO_ROOT / "boot/tamanna.inf", r"VERSION_STRING\s*=\s*[\d\.]+", f"VERSION_STRING                 = {VERSION}"),
    (REPO_ROOT / "boot/x200_100-efi/x2000_1000.inf", r"VERSION_STRING\s*=\s*[\d\.]+", f"VERSION_STRING                 = {VERSION}"),
    (REPO_ROOT / "boot/EFI/tamanna/tamanna.inf", r"VERSION_STRING\s*=\s*[\d\.]+", f"VERSION_STRING                 = {VERSION}"),
    (REPO_ROOT / "boot/x200_100-efi/tamanna.cfg", r"Version\s*=\s*[\d\.]+", f"Version    = {VERSION}"),
    (REPO_ROOT / "boot/distas/stable", r"Version:\s*[\d\.]+", f"Version: {VERSION}"),
    (ROOT / "tamanna_config.hm", r"version\s*=\s*\"[\d\.]+\"", f"version = \"{VERSION}\""),
    (REPO_ROOT / "bd-king-r7_auto-fix_code.json", r"\"version\"\s*:\s*\"[\d\.]+\"", f'"version": "{VERSION}"'),
    (REPO_ROOT / "tamanna/bd-king-r7_auto_code_fix.json", r"\"version\"\s*:\s*\"[\d\.]+\"", f'"version": "{VERSION}"'),
]


def update_file(path: Path, pattern: str, replacement: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text()
    new_text, n = re.subn(pattern, replacement, text)
    if n > 0 and new_text != text:
        bak = path.with_suffix(path.suffix + ".bak")
        path.write_text(new_text)
        bak.write_text(text)
        print(f"Updated {path} ({n} replacements)")
        return True
    return False


def main():
    changed = 0
    for file, pat, repl in REPLACEMENTS:
        if update_file(file, pat, repl):
            changed += 1
    print(f"Done. Central VERSION={VERSION}. Files updated: {changed}")


if __name__ == "__main__":
    main()
