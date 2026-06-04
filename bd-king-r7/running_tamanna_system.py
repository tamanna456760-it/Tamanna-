# ============================================================
#        🔥 ADVANCED TAMANNA LANGUAGE ACTIVATION ENGINE 🔥
# ============================================================

import time
import importlib
import traceback
import platform
import sys
from datetime import datetime

# ------------------------------------------------------------
# Utility: Color Output
# ------------------------------------------------------------
class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

def log(msg, color=Color.CYAN):
    print(color + msg + Color.RESET)

# ------------------------------------------------------------
# Utility: Timed Execution Wrapper
# ------------------------------------------------------------
def timed(label, func):
    start = time.time()
    result = func()
    end = time.time()
    log(f"⏱ {label} completed in {end - start:.3f}s", Color.YELLOW)
    return result

# ------------------------------------------------------------
# System Diagnostics
# ------------------------------------------------------------
def system_diagnostics():
    log("🔍 Running System Diagnostics...\n", Color.YELLOW)

    info = {
        "Python Version": sys.version.split()[0],
        "Platform": platform.system(),
        "Architecture": platform.machine(),
        "Timestamp": datetime.now().isoformat()
    }

    for k, v in info.items():
        log(f"• {k}: {v}", Color.GREEN)

    print()

# ------------------------------------------------------------
# Tamanna Activation
# ------------------------------------------------------------
def activate_tamanna():
    log("🎯 INITIALIZING TAMANNA CODE LANGUAGE...\n", Color.CYAN)

    system_diagnostics()

    try:
        # Try importing the main system
        def import_system():
            global tamanna_system
            tamanna_system = importlib.import_module("tamanna_system")

        timed("Module Import", import_system)
        log("✅ Tamanna system imported successfully!", Color.GREEN)

        # Start REPL
        def start_repl():
            global system
            system = tamanna_system.TamannaSystem()

        timed("REPL Boot", start_repl)
        log("🚀 Starting Tamanna REPL Environment...\n", Color.CYAN)

        # Test command
        test_code = 'লেখো "তামান্না সিস্টেম এখন সক্রিয়!"'
        system.interpreter.execute(test_code)

        log("\n🎉 TAMANNA CODE LANGUAGE IS NOW ACTIVE!", Color.GREEN)
        log("Available Features:", Color.CYAN)
        print("  • TK Token System")
        print("  • 7-Color Coding")
        print("  • .hm Files")
        print("  • Bangla + English syntax")
        print("  • Network capabilities")
        print("  • Dynamic REPL Engine")
        print("  • Auto Error Recovery\n")

    except Exception as e:
        log("❌ Activation error detected!", Color.RED)
        log(str(e), Color.RED)
        traceback.print_exc()

        log("\n🔄 Switching to SAFE MODE (Quick Tamanna)...\n", Color.YELLOW)

        # ------------------------------------------------------------
        # SAFE MODE: Minimal Working System
        # ------------------------------------------------------------
        class QuickTamanna:
            def __init__(self):
                log("🚀 Tamanna Quick Start Activated!", Color.GREEN)
                self.vars = {}

            def run(self):
                log("🧪 Running Safe Mode Demo...\n", Color.CYAN)
                print('তামান্না> লেখো "সিস্টেম প্রস্তুত!"')
                print("📢 সিস্টেম প্রস্তুত!")
                print('তামান্না> নির্ধারণ নাম = "তামান্না ইউজার"')
                print("💾 Variable 'নাম' = তামান্না ইউজার")
                print('তামান্না> লেখো "আসসালামু আলাইকুম: " + নাম')
                print("📢 আসসালামু আলাইকুম: তামান্না ইউজার")

        quick = QuickTamanna()
        quick.run()

# ------------------------------------------------------------
# Execute Activation
# ------------------------------------------------------------
activate_tamanna()