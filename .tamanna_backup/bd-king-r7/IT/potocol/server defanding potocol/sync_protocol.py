import json
from datetime import datetime

def make_packet(command, data=None):
    return json.dumps({
        "command": command,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data or {}
    })

def parse_packet(raw):
    return json.loads(raw)