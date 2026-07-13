import schedule
import time
import os

def job():
    os.system("python tamanna_book_sync.py")
    os.system("python tamanna_drive_sync.py")

schedule.every().day.at("02:00").do(job)

print("🔄 Tamanna AI Cloud Sync Running...")
while True:
    schedule.run_pending()
    time.sleep(60)