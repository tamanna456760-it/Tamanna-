import os
import stat

def unlock_all(folder):

    for root, dirs, files in os.walk(folder):

        for f in files:

            path = os.path.join(root, f)

            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    print("All files unlocked")


unlock_all(".")