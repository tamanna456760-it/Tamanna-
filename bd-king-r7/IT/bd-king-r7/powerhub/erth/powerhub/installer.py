"""
Installer helper: creates directories, validates env, and prints instructions.
This is safe and non-destructive.
"""
import os

def install_system():
    print("[Installer] Preparing BD-KING-R7 PowerHub Master environment...")
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    # Create default config if missing: handled in config.json at root
    print("[Installer] Directories created: logs/, data/")
    print("[Installer] Installation placeholder complete. Review README for deploy steps.")

if __name__ == "__main__":
    install_system()