from datetime import datetime

LOG_FILE = "security.log"


def write_log(event, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{timestamp}] [{level}] {event}"

    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


write_log("Tamanna Security System Started")
write_log("Monitoring Enabled")
write_log("Unauthorized access check active")
