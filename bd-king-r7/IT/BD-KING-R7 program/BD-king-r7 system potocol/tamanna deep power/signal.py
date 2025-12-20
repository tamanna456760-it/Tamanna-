def detect_intrusion(event):
    suspicious = ["unauthorized", "failed_login", "strange_ip", "file_change"]
    for key in suspicious:
        if key in event.lower():
            return True
    return False
def tamanna_defense(event):
    if detect_intrusion(event):
        return "Tamanna: সতর্ক! সন্দেহজনক কার্যকলাপ ধরা পড়েছে."
    else:
        return "Tamanna: সব ঠিক আছে, সিস্টেম শান্ত."
