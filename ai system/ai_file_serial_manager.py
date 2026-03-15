import os
from pathlib import Path

# Folder you want to organize
FOLDER_PATH = "./files"

def serial_rename(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files.sort()

    count = 1
    for file in files:
        ext = file.split(".")[-1]
        new_name = f"File_{count:03d}.{ext}"

        old_path = os.path.join(folder, file)
        new_path = os.path.join(folder, new_name)

        os.rename(old_path, new_path)
        print(f"{file} -> {new_name}")

        count += 1

def auto_create_folder():
    Path(FOLDER_PATH).mkdir(parents=True, exist_ok=True)

def run_ai_system():
    auto_create_folder()
    serial_rename(FOLDER_PATH)

if __name__ == "__main__":
    print("AI File Serial Manager Running...")
    run_ai_system()
    print("All files fixed and renamed in serial order.")