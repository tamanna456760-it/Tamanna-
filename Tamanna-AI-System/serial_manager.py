import os
from config import WATCH_FOLDER, SERIAL_PREFIX
from logger import log

def fix_serial(files):

    count = 1

    for file in files:

        old_path = os.path.join(WATCH_FOLDER, file)

        name, ext = os.path.splitext(file)

        new_name = f"{SERIAL_PREFIX}{count:03d}{ext}"

        new_path = os.path.join(WATCH_FOLDER, new_name)

        if old_path != new_path:
            os.rename(old_path, new_path)
            log(f"{file} -> {new_name}")

        count += 1