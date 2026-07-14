import time
import requests

GITHUB_TOKEN = "তোমার_গিটহাব_টোকেন"
REPO_OWNER = "tamanna456760-it"
REPO_NAME = "tamanna-"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def check_ai_system_health():
    ai_status_url = (
        "https://example.com/ai/status"  # AI সিস্টেমের স্ট্যাটাস এন্ডপয়েন্ট
    )
    response = requests.get(ai_status_url)
    if response.status_code == 200:
        status = response.json()
        if status["healthy"]:
            print("AI System is healthy.")
        else:
            print("AI System is unhealthy! Immediate attention required.")
    else:
        print(f"Failed to check AI system status: {response.status_code}")


def check_ai_sensing():
    ai_sensing_url = "https://example.com/ai/sensing"  # AI সেন্সিং ডেটা এন্ডপয়েন্ট
    response = requests.get(ai_sensing_url)
    if response.status_code == 200:
        sensing_data = response.json()
        print("AI Sensing Data:", sensing_data)
    else:
        print(f"Failed to fetch AI sensing data: {response.status_code}")


def check_ai_master_functionality():
    ai_master_url = "https://example.com/ai/master"  # মাস্টার AI ফাংশনের স্ট্যাটাস
    response = requests.get(ai_master_url)
    if response.status_code == 200:
        master_status = response.json()
        print("AI Master Functionality Status:", master_status)
        # তুমি চাইলে, এখানে মাস্টার AI-এর কাজের বিস্তারিত স্ক্যান করতে পারো
        # যেমন, কত লাইন কোডে AI অন্তর্ভুক্ত, কোনো কমিউনিকেশন ফেইল হয়েছে কিনা ইত্যাদি
    else:
        print(f"Failed to fetch AI master status: {response.status_code}")


def check_repo_and_ai():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        files = response.json()
        total_ai_lines = 0
        for file in files:
            if file["type"] == "file":
                file_url = file["url"]
                file_response = requests.get(file_url, headers=HEADERS)
                if file_response.status_code == 200:
                    content = file_response.json()["content"]
                    decoded_content = base64.b64decode(content).decode("utf-8")
                    # AI কোড লাইন গণনা বা চেকিং
                    ai_lines = decoded_content.count(
                        "AI"
                    )  # উদাহরণস্বরূপ, 'AI' লাইনগুলোর সংখ্যা গণনা করছি
                    total_ai_lines += ai_lines
        print(f"Total AI-related lines of code: {total_ai_lines}")
    else:
        print(f"Failed to fetch repo data: {response.status_code}")


if __name__ == "__main__":
    while True:
        check_repo_and_ai()  # গিটহাব ফাইল, AI সেন্সিং, AI হেল্থ, মাস্টার ফাংশনালিটি চেক হবে
        time.sleep(10)  # প্রতি ১০ সেকেন্ডে চেক করবে
