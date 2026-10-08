"""Lightweight web server wrapper."""

from __future__ import annotations

from typing import Any, Dict


class WebServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port

    def config(self) -> Dict[str, Any]:
        return {"host": self.host, "port": self.port, "status": "ready"}


web_server = WebServer()

__all__ = ["WebServer", "web_server"]
