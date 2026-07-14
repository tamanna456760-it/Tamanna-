import os
import shutil

ROOT = "."
DEST = {
    ".py": "runner/python",
    ".js": "runner/node",
    ".html": "runner/web",
    ".css": "runner/web",
    ".json": "runner/data",
    ".sh": "runner/shell",
}

os.makedirs("runner/python", exist_ok=True)
os.makedirs("runner/node", exist_ok=True)
os.makedirs("runner/web", exist_ok=True)
os.makedirs("runner/data", exist_ok=True)
os.makedirs("runner/shell", exist_ok=True)

for root, dirs, files in os.walk(ROOT):
    if root.startswith("./runner") or "/runner/" in root:
        continue

    for file in files:
        ext = os.path.splitext(file)[1].lower()

        if ext not in DEST:
            continue

        src = os.path.join(root, file)
        dst = os.path.join(DEST[ext], file)

        try:
            if os.path.abspath(src) != os.path.abspath(dst):
                shutil.move(src, dst)
                print(f"MOVED: {src} -> {dst}")
        except Exception as e:
            print(f"ERROR: {src} -> {e}")

print("DONE")
