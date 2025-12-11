import os

import requests
from msal import ConfidentialClientApplication

# Your Azure app credentials
CLIENT_ID = "your-client-id"
TENANT_ID = "your-tenant-id"
CLIENT_SECRET = "your-client-secret"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0/me/drive/root/children"

# Authenticate
app = ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)
token_response = app.acquire_token_for_client(scopes=SCOPE)
access_token = token_response["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}

# Create download folder
os.makedirs("OneDriveDownloads", exist_ok=True)

# Get list of files
response = requests.get(GRAPH_API_ENDPOINT, headers=headers)
files = response.json().get("value", [])

# Download each file
for file in files:
    if "@microsoft.graph.downloadUrl" in file:
        download_url = file["@microsoft.graph.downloadUrl"]
        file_name = file["name"]
        print(f"Downloading {file_name}...")
        file_data = requests.get(download_url)
        with open(os.path.join("OneDriveDownloads", file_name), "wb") as f:
            f.write(file_data.content)

print("✅ All files downloaded.")
