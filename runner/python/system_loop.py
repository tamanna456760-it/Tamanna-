import time
from datetime import datetime


def heartbeat():
    print("System heartbeat:", datetime.utcnow().isoformat() + "Z")

def check_status():
    print("System status: OK")

def run_system():
    print("System runner started.")
    last_beat = 0
    last_check = 0

    while True:
        now = time.time()

        if now - last_beat >= 5:
            heartbeat()
            last_beat = now

        if now - last_check >= 10:
            check_status()
            last_check = now

        time.sleep(1)

if __name__ == "__main__":
    run_system()
