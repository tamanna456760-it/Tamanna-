"""
Simple sync server that uses the PowerHubController to serve module state,
and provides lightweight set/get endpoints for devices to sync with master.
"""

import os
from pathlib import Path

from flask import jsonify, request, send_from_directory

from .core import PowerHubController, create_api_app


def run_sync_server(controller=None):
    # If controller not supplied, create one
    if controller is None:
        controller = PowerHubController()

    app = create_api_app(controller)

    # Additional sync endpoints
    @app.route("/sync/get", methods=["POST"])
    def sync_get():
        payload = request.get_json() or {}
        key = payload.get("key")
        if not key:
            return jsonify({"error": "no_key"}), 400

        modules = controller.list_modules()
        # If key is module.* return that module
        if key.startswith("module."):
            mname = key.split(".", 1)[1]
            m = modules.get(mname)
            if not m:
                return jsonify({"exists": False})
            return jsonify({"exists": True, "value": m})

        # fallback: return full store
        return jsonify({"exists": True, "value": modules})

    @app.route("/sync/set", methods=["POST"])
    def sync_set():
        payload = request.get_json() or {}
        key = payload.get("key")
        value = payload.get("value")
        if not key:
            return jsonify({"error": "no_key"}), 400

        # allow setting module state via sync
        if key.startswith("module."):
            mname = key.split(".", 1)[1]
            enabled = value.get("enabled") if isinstance(value, dict) else None
            metadata = value.get("metadata") if isinstance(
                value, dict) else None
            m = controller.set_module(
                mname, enabled=enabled, metadata=metadata)
            if not m:
                return jsonify({"error": "module_not_found"}), 404
            return jsonify({"synced": True, "module": m})

        # No generic persistent store here, so just echo back
        return jsonify({"synced": True, "key": key, "value": value})

    # Serve static web assets
    @app.route("/static/<path:filename>")
    def static_files(filename):
        base = Path(__file__).parent.parent / "web" / "static"
        return send_from_directory(str(base), filename)

    # Start Flask
    host = os.environ.get("PH_HOST", "0.0.0.0")
    port = int(os.environ.get("PH_PORT", "5000"))
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_sync_server()
