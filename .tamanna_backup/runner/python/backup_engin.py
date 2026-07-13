# Backup Engine
import shutil

def backup_file(src, dest):
    try:
        shutil.copy(src, dest)
        print(f"[BACKUP] {src} -> {dest}")
    except Exception as e:
        print(f"[BACKUP ERROR] {e}")

if __name__ == "__main__":
    backup_file("engin.py", "backup/engin.py")
