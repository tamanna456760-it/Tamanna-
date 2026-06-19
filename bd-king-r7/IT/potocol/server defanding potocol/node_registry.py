import json
from pathlib import Path

FILE = "data/nodes.json"

def save_nodes(nodes):
    Path("data").mkdir(exist_ok=True)

    with open(FILE, "w") as f:
        json.dump(nodes, f, indent=2)

def load_nodes():
    try:
        with open(FILE) as f:
            return json.load(f)
    except:
        return {}