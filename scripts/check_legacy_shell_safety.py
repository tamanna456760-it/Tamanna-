#!/usr/bin/env python3
"""Fail CI if quarantined legacy shell scripts become executable again."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUARANTINED = (
    "runner/shell/tamanna_github_backup.sh",
    "tamanna_code_editor_runner.sh",
    "runner/shell/auto_sync_all.sh",
    "~tamanna_code_editor_runner.sh",
    "runner/shell/bdking_r7_ultra.sh",
    "runner/shell/tamanna_auto_pro.sh",
    "runner/shell/tamanna_ultra_ai.sh",
    "runner/shell/tamanna_ultra_pro.sh",
    "runner/shell/tamanna_ultra_max.sh",
    "runner/shell/tamanna_autonomous.sh",
    "runner/shell/tamanna_all_in_one.sh",
    "runner/shell/tamanna_multi_user.sh",
    "runner/shell/tamanna_enterprise.sh",
    "runner/shell/tamanna_ultra_24x7.sh",
    "runner/shell/tamanna_full_backup.sh",
    "runner/shell/tamanna_ultra_cloud.sh",
    "runner/shell/tamanna_ultra_pro_cli.sh",
    "runner/shell/tamanna_self_learning.sh",
    "runner/shell/tamanna_ultra_ai_full.sh",
    "runner/shell/tamanna_ultra_extreme.sh",
    "runner/shell/tamanna_ultra_powerhub.sh",
    "runner/shell/tamanna_ultra_fileinfo.sh",
    "runner/shell/tamanna_ultra_advanced.sh",
    "runner/shell/tamanna_ultra_firewall.sh",
    "runner/shell/tamanna_code_auto_comm.sh",
    "runner/shell/tamanna_ultimate_cloud.sh",
    "runner/shell/tamanna_ultra_real_time.sh",
    "runner/shell/tamanna_success_program.sh",
    "runner/shell/bdking_r7_tamanna_ultra.sh",
    "runner/shell/tamanna_ultra_all_in_one.sh",
    "runner/shell/tamanna_ultra_mobile_alert.sh",
    "runner/shell/check_token.sh",
    ".github/workflows/hakar_lock.sh",
    ".github/workflows/tamanna_defender.sh",
    ".github/workflows/tamanna_syber_shield.sh",
    ".github/workflows/tamanna_ultra_defense.sh",
    ".github/workflows/tamanna_auto_defender.sh",
)


def main() -> int:
    failures = []
    for relative in QUARANTINED:
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"missing quarantine guard: {relative}")
            continue
        content = path.read_text(encoding="utf-8")
        if "SAFETY HOLD" not in content or "exit 2" not in content:
            failures.append(f"legacy script is no longer fail-closed: {relative}")
    if failures:
        print("FAIL: unsafe legacy script guard check")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"PASS: all {len(QUARANTINED)} unsafe legacy scripts remain fail-closed.")
    print("No scripts were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
