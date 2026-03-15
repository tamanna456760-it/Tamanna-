import shutil, os
from config import GIT_REPO_PATH, BACKUP_PATH
from logger import log

def backup_files():
    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)
    
    for f in os.listdir(GIT_REPO_PATH):
        src = os.path.join(GIT_REPO_PATH, f)
        dst = os.path.join(BACKUP_PATH, f)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
    log("Backup completed")