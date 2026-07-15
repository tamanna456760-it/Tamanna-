import os

from logger import log


def git_commit_push():
    os.system("git add .")
    os.system('git commit -m "Auto commit by Tamanna AI System"')
    os.system("git push")
    log("Git repo synced successfully")