# tamanna_installer.py
import os
import subprocess

# --------------------------
# 1️⃣ Folder Structure Setup
# --------------------------
folders = [
    "Tamanna/bd-king-r7/boot/tools",
    "Tamanna/bd-king-r7/boot/tools/logs",
    "Tamanna/bd-king-r7/boot/tools/sync/backup",
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

# --------------------------
# 2️⃣ Create log files
# --------------------------
log_files = [
    "system_log.txt",
    "device_status.txt",
    "system_resources.txt",
    "network_log.txt",
]

for log_file in log_files:
    path = f"Tamanna_System/logs/{log_file}"
    if not os.path.exists(path):
        open(path, "w").close()
        print(f"Created log file: {path}")

# --------------------------
# 3️⃣ Install dependencies
# --------------------------
try:
    import psutil

    print("psutil already installed")
except ImportError:
    print("Installing psutil...")
    subprocess.check_call(["pip", "install", "psutil"])

# --------------------------
# 4️⃣ Create master script run_all.py
# --------------------------
run_all_code = """import subprocess

scripts = [
    "system_log.py",
    "device_monitor.py",
    "system_resources.py",
    "network_monitor.py",
    "backup_logs.py"
]

for script in scripts:
    subprocess.run(["python", script])
"""

run_all_path = "Tamanna_System/boot_tools/run_all.py"
with open(run_all_path, "w") as f:
    f.write(run_all_code)
print(f"Created master script: {run_all_path}")

# --------------------------
# 5️⃣ Create README.md
# --------------------------
readme_content = """# Tamanna System

**Tamanna System** is a multi-device monitoring and logging system.
It monitors devices, system resources, network, and keeps backups.

## Folder Structure
Tamanna_System/
├── boot_tools/        # All Python scripts
├── logs/              # All log files
├── sync/backup/       # Backups
└── README.md

## Usage
1. Add your IPs to device_monitor.py
2. Run master script:
   python boot_tools/run_all.py
3. Check logs in logs/ folder
4. Backups will be in sync/backup/

"""

readme_path = "Tamanna_System/README.md"
with open(readme_path, "w") as f:
    f.write(readme_content)
print(f"Created README: {readme_path}")

print("\n✅ Tamanna System installation complete!")
