#!/usr/bin/env python3
import logging
import signal
import sys
import threading
import time

from flask import Flask, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

stop_event = threading.Event()
worker_status = {"last_run": None, "runs": 0, "error": None}


def do_work_loop():
    while not stop_event.is_set():
        try:
            # ---- replace this with your real build tasks ----
            logging.info("Running PowerHub worker iteration...")
            # example: scan repo, build artifacts, run tests, pack files...
            worker_status["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
            worker_status["runs"] += 1
            time.sleep(5)
        except Exception as e:
            logging.exception("Worker error")
            worker_status["error"] = str(e)
            time.sleep(5)


worker_thread = threading.Thread(target=do_work_loop, daemon=True)


@app.route("/health")
def health():
    ok = not stop_event.is_set()
    payload = {"status": "ok" if ok else "stopping", **worker_status}
    return jsonify(payload), 200 if ok else 503


def start_worker():
    logging.info("Starting worker thread")
    worker_thread.start()


def stop_handler(signum, frame):
    logging.info("Signal received, stopping gracefully...")
    stop_event.set()
    worker_thread.join(timeout=10)
    logging.info("Worker stopped. Exiting.")
    sys.exit(0)


if __name__ == "__main__":
    import os

    from waitress import serve  # production WSGI server

    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)
    start_worker()
    port = int(os.environ.get("PORT", "8080"))
    # Serve Flask via waitress (production)
    serve(app, host="0.0.0.0", port=port, threads=4)
