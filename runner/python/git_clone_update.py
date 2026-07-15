import os

from logger import log

GIT_REPO_URL = "https://vscode.dev/github/tamanna456760-it/Tamanna-"
LOCAL_PATH = "./Tamanna-"

def git_setup():
    if not os.path.exists(LOCAL_PATH):
        os.system(f"git clone {GIT_REPO_URL} {LOCAL_PATH}")
        log("Git repo cloned successfully")
    else:
        os.chdir(LOCAL_PATH)
        os.system("git pull")
        log("Git repo updated successfully")