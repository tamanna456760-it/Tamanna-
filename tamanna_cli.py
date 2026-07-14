#!/usr/bin/env python3

import argparse
import json

try:
    from ai_brain_core import TamannaBrain
except ImportError:
    TamannaBrain = None

try:
    from ai_system_monitor import AISystemMonitor
except ImportError:
    AISystemMonitor = None

try:
    from tamanna_security_ai import TamannaSecurityAI
except ImportError:
    TamannaSecurityAI = None


def cmd_status():
    if TamannaBrain:
        brain = TamannaBrain()
        print(json.dumps(brain.info(), indent=4))
    else:
        print("Brain module not found.")


def cmd_health():
    if AISystemMonitor:
        monitor = AISystemMonitor()
        print(json.dumps(monitor.generate_report(), indent=4))
    else:
        print("System monitor not found.")


def cmd_security():
    if TamannaSecurityAI:
        security = TamannaSecurityAI()
        print(json.dumps(security.generate_report(), indent=4))
    else:
        print("Security module not found.")


def main():
    parser = argparse.ArgumentParser(
        prog="tamanna",
        description="Tamanna System CLI"
    )

    parser.add_argument(
        "command",
        choices=[
            "status",
            "health",
            "security"
        ],
        help="Command to execute"
    )

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()

    elif args.command == "health":
        cmd_health()

    elif args.command == "security":
        cmd_security()


if __name__ == "__main__":
    main()
