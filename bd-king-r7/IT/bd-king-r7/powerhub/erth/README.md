# Earth BD-KING-R7 PowerHub Master

This repository is an integrated, **safe** control & sync system for the BD-KING-R7 PowerHub modules:
Network Spirit, HighPower Engine, Supersonic Power, and BD-KING-R7 Core.

It includes:

- PowerHub core controller (modules & persistent state)
- Simple sync API for devices
- Web UI to toggle modules
- Builder & installer helper scripts
- Config template

> **Note:** This system is meant for your own devices and development. Do not use it to access devices you don't own.

## Quick start (local)

1. Clone repo and `cd` into it.
2. Create a Python venv and install deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
