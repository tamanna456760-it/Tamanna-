import time
import schedule
from core.book_sync import sync_books
from core.drive_sync import upload_books

def full_cycle():
    print("⚙ Tamanna AI Head Cycle Started")
    sync_books()
    upload_books()
    print("✅ Cycle Completed")

schedule.every(6).hours.do(full_cycle)

def run_forever():
    full_cycle()
    while True:
        schedule.run_pending()
        time.sleep(60)