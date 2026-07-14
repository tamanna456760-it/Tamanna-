import logging
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    filename="logs/server.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def log_event(msg):
    logging.info(msg)
