import os
from datetime import datetime
from config import LOG_FOLDER

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

log_file = os.path.join(LOG_FOLDER, "system.log")

def log(message):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a") as f:
        f.write(f"[{time}] {message}\n")

    print(message)