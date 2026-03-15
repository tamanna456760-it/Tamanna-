import time
from config import SCAN_INTERVAL
from file_scanner import scan_files
from serial_manager import fix_serial
from logger import log

def run_ai():

    log("Tamanna AI System Started")

    while True:

        files = scan_files()

        if files:
            fix_serial(files)

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    run_ai()