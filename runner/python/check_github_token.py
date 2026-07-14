import requests

token = "tamanna"

headers = {"Authorization": f"token {token}"}

response = requests.get("https://api.github.com/user", headers=headers)

if response.status_code == 200:
    print("✅ Token working!")
    print(response.json())
else:
    print("❌ Token not working")
    print(response.status_code, response.text)
