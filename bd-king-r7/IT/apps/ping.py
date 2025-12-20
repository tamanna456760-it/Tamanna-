import os

host = "google.com"
response = os.system("ping -c 1 " + host)

if response == 0:
    print("Ping OK ✅")
else:
    print("Ping Failed ❌")