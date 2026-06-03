from core.firewall_core import FirewallCore
from core.threat_intel import ThreatIntel
from core.protocol_master import ProtocolMaster
import random
import time

# node server connection
NODE_URL = "http://localhost:3000"

firewall = FirewallCore(NODE_URL)
intel = ThreatIntel()
master = ProtocolMaster(firewall, intel)

# simulation attack traffic
fake_ips = ["1.1.1.1", "2.2.2.2", "3.3.3.3"]

print("🔥 Tamanna Firewall Starting...")

while True:
    ip = random.choice(fake_ips)

    firewall.log(ip)

    result = master.process(ip)

    print(f"IP: {ip} | STATUS: {result}")

    time.sleep(0.5)