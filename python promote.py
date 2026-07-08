import os
import requests

username = os.environ["@lably772"]
webhook = os.environ["https://vt.tiktok.com/ZS9MBnETxpcpR-PpGmD/"]

message = {
    "content": (
        f"🔴 I'm LIVE on TikTok!\n"
        f"https://www.tiktok.com/@{@lably772}/live\n\n"
        "Come join the stream!"
    )
}

requests.post(webhook, json=message, timeout=15)
print("Notification sent.")