# network_monitor.py
import psutil
import datetime

net_io = psutil.net_io_counters()
with open("../logs/network_log.txt", "a") as f:
    f.write(
        f"{datetime.datetime.now()} | Sent: {net_io.bytes_sent} | Received: {net_io.bytes_recv}\n"
    )

print("Network monitoring complete.")
