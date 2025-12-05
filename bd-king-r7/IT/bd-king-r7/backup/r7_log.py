# Append inside r7_backup.py after each file copy
with open(os.path.join(session_dir, "affirm.log"), "a", encoding="utf-8") as log:
    log.write(f"{entry['path']} | SHA256={h}\n")
