# run_all.py
import subprocess

scripts = [
    "system_log.py",
    "device_monitor.py",
    "system_resources.py",
    "network_monitor.py",
    "backup_logs.py",
]

for script in scripts:
    subprocess.run(["python", script])
