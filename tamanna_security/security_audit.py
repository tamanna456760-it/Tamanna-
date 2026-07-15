#!/usr/bin/env python3

import hashlib
import os
import socket
from datetime import datetime

print("=== Tamanna AI Security Audit ===")

host = socket.gethostname()
ip = socket.gethostbyname(host)

print("Host:", host)
print("IP:", ip)

files = []
for root, dirs, fs in os.walk("."):
    for f in fs:
        if f.endswith((".py",".js",".yml",".json")):
            path=os.path.join(root,f)
            files.append(path)

print("Files scanned:", len(files))

for f in files[:20]:
    try:
        h=hashlib.sha256(open(f,"rb").read()).hexdigest()
        print(f, h[:16])
    except:
        pass

print("Time:", datetime.now())
print("Audit Complete")
