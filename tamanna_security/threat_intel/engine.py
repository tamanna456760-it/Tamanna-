#!/usr/bin/env python3

import datetime
import hashlib
import json
import os

BASE="tamanna_security/threat_intel"

report={
    "system":"Tamanna AI Threat Intelligence Engine",
    "mode":"DEFENSIVE",
    "time":str(datetime.datetime.now()),
    "checks":[]
}

# File integrity check
for root,dirs,files in os.walk("."):
    for f in files:
        if f.endswith((".py",".js",".json",".yml")):
            path=os.path.join(root,f)
            try:
                h=hashlib.sha256(open(path,"rb").read()).hexdigest()
                report["checks"].append({
                    "file":path,
                    "hash":h[:32]
                })
            except:
                pass

os.makedirs(BASE+"/reports",exist_ok=True)

with open(BASE+"/reports/security_report.json","w") as f:
    json.dump(report,f,indent=4)

print("Tamanna AI Threat Intelligence Report Generated")
