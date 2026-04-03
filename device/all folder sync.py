import os
import time
import firebase_admin
from firebase_admin import credentials, storage

# Firebase setup
cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'YOUR_PROJECT.appspot.com'
})
bucket = storage.bucket()

# Folder to sync (example: Internal Storage)
root_dir = "/sdcard"  # Termux path

def sync_folder(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                blob_path = os.path.relpath(file_path, root_dir)
                blob = bucket.blob(blob_path)
                blob.upload_from_filename(file_path)
                print(f"Uploaded: {blob_path}")
            except Exception as e:
                print(f"Error uploading {file_path}: {e}")

while True:
    sync_folder(root_dir)
    print("Sync cycle complete. Waiting 30s...")
    time.sleep(30)  # sync every 30 seconds