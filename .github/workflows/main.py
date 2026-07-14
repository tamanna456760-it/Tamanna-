# main.py

import os


def run_all_modules():
    print("🚀 AI System Starting...")

    # Example import
    try:
        import models
        import utils

        print("Modules Loaded Successfully")
    except Exception as e:
        print("Module Error:", e)

    # আপনার আসল AI কোড এখানে বসাবেন
    print("AI System Running...")


if __name__ == "__main__":
    run_all_modules()
