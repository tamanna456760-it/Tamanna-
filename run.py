#!/usr/bin/env python3

from datetime import datetime

print("=" * 50)
print("🚀 TAMANNA SYSTEM")
print("=" * 50)
print(f"Started : {datetime.now()}")

# Health Check
try:
    from tools.health_check import system_health
    print("\n[Health Check]")
    print(system_health())
except Exception as e:
    print(f"Health check unavailable: {e}")

# Environment Info
try:
    from tools.env_check import environment_info
    print("\n[Environment]")
    print(environment_info())
except Exception as e:
    print(f"Environment info unavailable: {e}")

# Logger
try:
    from tools.logger import log
    log("Tamanna System started successfully.")
    print("\nLog written to system.log")
except Exception as e:
    print(f"Logger unavailable: {e}")

print("\n✅ Tamanna System is running.")
print("=" * 50)
