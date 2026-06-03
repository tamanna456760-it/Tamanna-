import os
import base64
import requests
import time

GITHUB_TOKEN = 'তোমার_গিটহাব_টোকেন'
REPO_OWNER = 'tamanna456760-it'
REPO_NAME = 'tamanna-'

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def insert_ip_mac_into_code(code):
    ip_address = '192.168.1.1'  # উদাহরণ আইপি
    mac_address = '00:1A:2B:3C:4D:5E'  # উদাহরণ MAC
    header = f'// IP: {ip_address}, MAC: {mac_address}\n'
    return header + code

def communicate_with_ai_master(data):
    ai_master_url = 'https://example.com/ai/master_report'  # মাস্টার AI এন্ডপয়েন্ট
    response = requests.post(ai_master_url, json=data)
    if response.status_code == 200:
        print('AI Master received report successfully.')
    else:
        print(f'Failed to report to AI Master: {response.status_code}')

def scan_and_update_repo():
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        files = response.json()
        ai_report = []
        for file in files:
            if file['type'] == 'file':
                file_url = file['url']
                file_response = requests.get(file_url, headers=HEADERS)
                if file_response.status_code == 200:
                    content = file_response.json()['content']
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    updated_content = insert_ip_mac_into_code(decoded_content)
                    # আপডেট করা কোড আবার আপলোড করা হচ্ছে
                    update_url = file_url
                    update_response = requests.put(update_url, headers=HEADERS, json={
                        'message': f'Inject IP and MAC to {file["path"]}',
                        'content': base64.b64encode(updated_content.encode()).decode('utf-8'),
                        'branch': 'main'  # সঠিক ব্রাঞ্চ নির্ধারণ করতে হবে
                    })
                    if update_response.status_code == 200:
                        print(f'Updated file: {file["path"]}')
                    else:
                        print(f'Failed to update file: {file["path"]}, status: {update_response.status_code}')
                    ai_report.append({
                        'file': file['path'],
                        'status': 'updated'
                    })
                else:
                    print(f'Failed to fetch file: {file["path"]}, status: {file_response.status_code}')
                    ai_report.append({
                        'file': file['path'],
                        'status': 'fetch_failed'
                    })
        communicate_with_ai_master(ai_report)  # AI মাস্টারকে রিপোর্ট পাঠানো হচ্ছে
    else:
        print(f'Failed to fetch repo data: {response.status_code}')

if __name__ == "__main__":
    while True:
        scan_and_update_repo()  # প্রতি 10 সেকেন্ডে পুরো রিপোজিটরি স্ক্যান হবে
        time.sleep(10)  # 10 সেকেন্ড অপেক্ষা করে পুনরায় চালু হবে