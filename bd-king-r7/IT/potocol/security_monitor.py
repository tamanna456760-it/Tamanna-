import re
from collections import Counter

counter = Counter()

with open("security.log", "r", encoding="utf-8") as f:
    for line in f:
        m = re.search(r"IP=([0-9.]+)", line)
        if m:
            counter[m.group(1)] += 1

for ip, count in counter.most_common(20):
    if count > 100:
        print(f"ALERT: {ip} -> {count} requests")