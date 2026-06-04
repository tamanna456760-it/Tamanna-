# quick_start.py
from akon_tamanna_sync import AkonCodeMonitor

# Setup auto-sync for your project
monitor = AkonCodeMonitor(
    watch_dirs=["./src", "./scripts", "./akon_code"], build_dir="./build_output"
)

# Start monitoring
monitor.start_monitoring()
