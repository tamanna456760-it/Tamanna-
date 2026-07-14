"""
PowerHub core modules and controller.
This is application logic only — safe control and simulation of modules.
"""

import json
import json as _json

# Load config
import threading
import time
from pathlib import Path
from typing import Dict

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

_cfg_path = Path(__file__).parent.parent / "config.json"
if _cfg_path.exists():
    cfg = _json.loads(_cfg_path.read_text())
else:
    cfg = {}

STORE_FILE = cfg.get("storage_file", "powerhub_store.json")


def _now_ts():
    return int(time.time())


class ModuleState:
    def __init__(self, name: str):
        self.name = name
        self.enabled = False
        self.last_update = _now_ts()
        self.metadata = {}

    def to_dict(self):
        return {
            "name": self.name,
            "enabled": self.enabled,
            "last_update": self.last_update,
            "metadata": self.metadata,
        }

    def update(self, enabled=None, metadata=None):
        if enabled is not None:
            self.enabled = bool(enabled)
        if metadata is not None:
            self.metadata.update(metadata)
        self.last_update = _now_ts()


class PowerHubController:
    def __init__(self):
        # Create core modules
        self.modules: Dict[str, ModuleState] = {
            "network_spirit": ModuleState("network_spirit"),
            "highpower_engine": ModuleState("highpower_engine"),
            "supersonic_power": ModuleState("supersonic_power"),
            "bdkingr7_core": ModuleState("bdkingr7_core"),
        }
        self._lock = threading.Lock()
        self._load_from_disk()

    def list_modules(self):
        with self._lock:
            return {k: v.to_dict() for k, v in self.modules.items()}

    def get_module(self, name):
        with self._lock:
            m = self.modules.get(name)
            return m.to_dict() if m else None

    def set_module(self, name, enabled=None, metadata=None):
        with self._lock:
            if name not in self.modules:
                return None
            self.modules[name].update(enabled=enabled, metadata=metadata or {})
            self._save_to_disk()
            return self.modules[name].to_dict()

    def toggle_module(self, name):
        with self._lock:
            if name not in self.modules:
                return None
            m = self.modules[name]
            m.update(enabled=not m.enabled)
            self._save_to_disk()
            return m.to_dict()

    def _save_to_disk(self):
        try:
            data = {k: v.to_dict() for k, v in self.modules.items()}
            Path(STORE_FILE).write_text(
                json.dumps({"saved_at": _now_ts(), "modules": data}, indent=2)
            )
        except Exception as e:
            print("[PowerHubController] Save error:", e)

    def _load_from_disk(self):
        p = Path(STORE_FILE)
        if not p.exists():
            return
        try:
            raw = json.loads(p.read_text())
            for k, v in raw.get("modules", {}).items():
                if k in self.modules:
                    self.modules[k].enabled = v.get("enabled", False)
                    self.modules[k].last_update = v.get("last_update", _now_ts())
                    self.modules[k].metadata = v.get("metadata", {})
        except Exception as e:
            print("[PowerHubController] Load error:", e)


# Small convenience for direct run: expose a Flask API for controller.
def create_api_app(controller: PowerHubController):
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent.parent / "web" / "templates"),
    )
    CORS(app)

    @app.route("/")
    def home():
        # Return UI template (web client)
        return render_template("index.html")

    @app.route("/api/modules", methods=["GET"])
    def list_modules():
        return jsonify(controller.list_modules())

    @app.route("/api/module/<name>", methods=["GET"])
    def get_module(name):
        m = controller.get_module(name)
        if not m:
            return jsonify({"error": "not_found"}), 404
        return jsonify(m)

    @app.route("/api/module/<name>/toggle", methods=["POST"])
    def toggle(name):
        m = controller.toggle_module(name)
        if not m:
            return jsonify({"error": "not_found"}), 404
        return jsonify(m)

    @app.route("/api/module/<name>/set", methods=["POST"])
    def set_module(name):
        payload = request.get_json() or {}
        enabled = payload.get("enabled")
        metadata = payload.get("metadata")
        m = controller.set_module(name, enabled=enabled, metadata=metadata)
        if not m:
            return jsonify({"error": "not_found"}), 404
        return jsonify(m)

    return app
