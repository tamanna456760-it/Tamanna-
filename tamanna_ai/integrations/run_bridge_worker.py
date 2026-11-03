"""Run the bridge worker against Tamanna AI's configured model provider."""
import asyncio
import inspect
import os
import time

from tamanna_ai.integrations.bridge_worker import TamannaBridgeWorker

def run_awaitable(value):
    if not inspect.isawaitable(value):
        return value
    result = {"value": None, "error": None}
    def target():
        try:
            result["value"] = asyncio.run(value)
        except Exception as exc:
            result["error"] = exc
    import threading
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join()
    if result["error"] is not None:
        raise result["error"]
    return result["value"]

def tamanna_handler(message, conversation_id):
    # Reuse the same provider configured by the existing Tamanna chat server.
    from Main import get_model_provider
    provider = get_model_provider()
    return str(run_awaitable(provider.generate(message)))

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
            # Do not log message contents, credentials, or provider responses.
            print("[TAMANNA BRIDGE WORKER] Error:", type(exc).__name__, flush=True)
            time.sleep(max(5, poll_seconds))

if __name__ == "__main__":
    main()
