import os
import requests
from tqdm import tqdm

BASE_DIR = "tamanna_ai_books"

BOOK_SOURCES = {
    "Python": [
        "https://assets.openstax.org/oscms-prodcms/media/documents/Introduction_to_Python_Programming_-_WEB.pdf"
    ],
    "General_Programming": [
        "https://dl.ojocv.gov.et/admin_/book/coding-for-beginners-in-easy-steps-basic-programming-for-all-ages.pdf"
    ]
}

def download_pdf(url, folder):
    os.makedirs(folder, exist_ok=True)
    filename = url.split("/")[-1]
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        print(f"✔ Already synced: {filename}")
        return

    response = requests.get(url, stream=True)
    total = int(response.headers.get("content-length", 0))

    with open(path, "wb") as file, tqdm(
        desc=filename,
        total=total,
        unit="B",
        unit_scale=True
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            bar.update(len(data))

    print(f"✅ Synced: {filename}")

def sync_books():
    for category, urls in BOOK_SOURCES.items():
        folder = os.path.join(BASE_DIR, category)
        for url in urls:
            download_pdf(url, folder)

if __name__ == "__main__":
    print("🤖 Tamanna AI Book Sync Started")
    sync_books()
    print("✅ Tamanna AI Book Sync Completed")