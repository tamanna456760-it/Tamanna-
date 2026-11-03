"""Run the bridge worker against Tamanna AI's configured model provider."""
import asyncio
import os
import time
from pathlib import Path

from dotenv import load_dotenv

# The worker is a separate process from Main.py, so load the same private env file.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)

from tamanna_ai.integrations.bridge_worker import TamannaBridgeWorker


def tamanna_handler(message, conversation_id):
    # Use the exact provider factory used by Main.py's authenticated /api/chat route.
    from tamanna_ai.integrations.provider import get_model_provider

    provider = get_model_provider()
    reply = asyncio.run(provider.generate(message))
    if not isinstance(reply, str) or not reply.strip():
        raise RuntimeError("Tamanna model provider returned an empty reply")
    return reply


def main():
    worker = TamannaBridgeWorker(handler=tamanna_handler)
    poll_seconds = max(1, float(os.getenv("TAMANNA_BRIDGE_POLL_SECONDS", "3")))
    while True:
        try:
            result = worker.process_one()
            if result.get("status") == "empty":
                time.sleep(poll_seconds)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            # Never log message contents, credentials, or provider responses.
            print("[TAMANNA BRIDGE WORKER] Error:", type(exc).__name__, flush=True)
            time.sleep(max(5, poll_seconds))


if __name__ == "__main__":
    main()
