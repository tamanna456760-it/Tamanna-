import datetime
import json
import os

report = {
    "system": "Tamanna AI Dark Web Intelligence",
    "mode": "defensive analysis",
    "time": str(datetime.datetime.now()),
    "modules": [
        "Threat Intelligence",
        "Privacy Analysis",
        "Security Awareness",
        "Risk Reporting"
    ]
}

os.makedirs("tamanna_security/darkweb_intel/reports", exist_ok=True)

with open("tamanna_security/darkweb_intel/reports/report.json","w") as f:
    json.dump(report,f,indent=4)

print("Tamanna AI Intelligence Report Created")
