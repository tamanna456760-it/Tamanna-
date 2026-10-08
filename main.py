"""Compatibility entry point for the Tamanna AI FastAPI app.

This file keeps the existing `Main.py` implementation intact while providing the
expected `python3 main.py` launch path requested by the project workflow.
"""

import os

import uvicorn

from Main import app


def main() -> None:
    """Start the FastAPI server with project-safe defaults.

    The existing project already defines the application in `Main.py`; this wrapper
    provides the conventional lowercase entry point without modifying the original
    app implementation or creating a duplicate server.
    """
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload_mode = os.getenv("RELOAD", "0").lower() in {"1", "true", "yes", "on"}

    uvicorn.run(app, host=host, port=port, reload=reload_mode)


if __name__ == "__main__":
    main()
