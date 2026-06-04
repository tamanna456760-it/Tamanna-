import json

with open("run.json", "r") as f:
    data = json.load(f)

print("JSON Data:")
print(data)