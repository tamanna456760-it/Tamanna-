import os
from config import WATCH_FOLDER

def scan_files():
    if not os.path.exists(WATCH_FOLDER):
        os.makedirs(WATCH_FOLDER)

    files = []

    for f in os.listdir(WATCH_FOLDER):
        path = os.path.join(WATCH_FOLDER, f)

        if os.path.isfile(path):
            files.append(f)

    files.sort()
    return files