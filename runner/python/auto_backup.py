# auto_backup.py
import datetime
import shutil

src_folders = ["boot_tools", "logs"]
backup_folder = (
    f"sync/backup/backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

shutil.os.makedirs(backup_folder)

for folder in src_folders:
    shutil.copytree(folder, f"{backup_folder}/{folder}")

print(f"Backup completed at {backup_folder}")
