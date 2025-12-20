def detect_intrusion(event):
    suspicious = ["unauthorized", "failed_login", "strange_ip", "file_change"]
    for key in suspicious:
        if key in event.lower():
            return True
    return False
