# integrated_system.py
from akon_tamanna_sync import AkonCodeMonitor, AkonBuildSystem
import threading

class IntegratedAkonSystem:
    def __init__(self):
        self.monitor = AkonCodeMonitor(["./src"])
        self.builder = AkonBuildSystem()
        
    def start(self):
        # Build first
        self.builder.build_project()
        
        # Then start monitoring
        self.monitor.start_monitoring()
        
        print("Integrated Akon System running...")
        
    def stop(self):
        self.monitor.stop_monitoring()

# Usage
system = IntegratedAkonSystem()
system.start()