#!/usr/bin/env python3
"""
Google Drive Sync
"""
import os
import pickle
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class GoogleDriveSync:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
    
    def sync_files(self):
        print("🔄 Syncing with Google Drive...")
        
        # Sync JSON files
        for file in os.listdir('.'):
            if file.endswith('.json'):
                self.upload_file(file)
        
        print("✅ Google Drive sync completed!")
    
    def upload_file(self, file_path):
        try:
            file_metadata = {'name': file_path}
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"✅ Uploaded: {file_path} (ID: {file.get('id')})")
            
        except Exception as e:
            print(f"❌ Failed to upload {file_path}: {e}")

def main():
    if os.path.exists('credentials.json'):
        sync = GoogleDriveSync()
        sync.sync_files()
    else:
        print("⚠️ Google credentials not found, skipping sync")

if __name__ == "__main__":
    main()