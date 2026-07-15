import os
import time

import schedule


def job():
    os.system("python tamanna_book_sync.py")

schedule.every().day.at("03:00").do(job)

print("🕒 Tamanna AI Auto Sync Running...")
while True:
    schedule.run_pending()
    time.sleep(60)