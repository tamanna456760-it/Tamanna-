import logging
import os

# ensure log directory exists
log_dir = "ROOT/logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "tamanna_pro_cli.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

logging.info("💠 [BOOT] Tamanna CLI started")
logging.info("🌍 [SYSTEM] Logging system initialized")

print("Tamanna CLI running...")