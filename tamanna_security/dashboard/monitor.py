#!/usr/bin/env python3

import os
import json
import datetime
import subprocess

BASE="tamanna_security/dashboard"

report={
    "system":"Tamanna AI Security Dashboard",
    "time":str(datetime.datetime.now()),
    "checks":{}
}

# System check
try:
    report["checks"]["disk"] = subprocess.getoutput("df -h")
except:
    report["checks"]["disk"]="error"

# Project file count
count=0
for root,dirs,files in os.walk("."):
    count += len(files)

report["checks"]["project_files"]=count

# Domain check (নিজের domain)
try:
    domain=subprocess.getoutput("curl -I -L --max-time 10 https://www.tamanna.com")
    report["checks"]["domain_status"]=domain[:500]
except:
    report["checks"]["domain_status"]="failed"

os.makedirs(BASE+"/reports",exist_ok=True)

with open(BASE+"/reports/dashboard_report.json","w") as f:
    json.dump(report,f,indent=4)

print("Tamanna AI Dashboard Report Created")
