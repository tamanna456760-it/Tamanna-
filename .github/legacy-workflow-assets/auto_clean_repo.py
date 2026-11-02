import hashlib
import os
import shutil

ROOT_DIR = "./"   # repo root
DUP_FOLDER = "./_duplicates_removed"
SORTED_FOLDER = "./_sorted"

os.makedirs(DUP_FOLDER, exist_ok=True)
os.makedirs(SORTED_FOLDER, exist_ok=True)

file_hashes = {}

def get_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def move_sorted(filepath):
    ext = filepath.split(".")[-1]
    target_folder = os.path.join(SORTED_FOLDER, ext)
    os.makedirs(target_folder, exist_ok=True)
    shutil.copy(filepath, target_folder)

def scan_and_clean():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith((".py", ".js", ".html", ".css")):
                full_path = os.path.join(root, file)

                file_hash = get_hash(full_path)

                if file_hash in file_hashes:
                    print(f"Duplicate Found: {full_path}")
                    shutil.move(full_path, DUP_FOLDER)
                else:
                    file_hashes[file_hash] = full_path
                    move_sorted(full_path)

if __name__ == "__main__":
    scan_and_clean()
    print("✅ Scan Complete")