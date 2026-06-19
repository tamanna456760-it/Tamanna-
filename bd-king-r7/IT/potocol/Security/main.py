import socket
import json
import threading
from datetime import datetime

from auth_manager import verify
from rate_limiter import RateLimiter
from event_logger import log_event
from attack_detector import AttackDetector
from auto_sync import AutoSync

HOST = "0.0.0.0"
PORT = 9000

rate_limiter = RateLimiter(limit=20)
detector = AttackDetector()
sync = AutoSync()

# Active nodes
nodes = {}

def build_response(status, message, data=None):
    return json.dumps({
        "status": status,
        "message": message,
        "time": datetime.utcnow().isoformat(),
        "data": data or {}
    })


def handle_client(conn, addr):
    ip = addr[0]
    log_event(f"Connection from {ip}")

    try:
        raw = conn.recv(4096).decode()

        # Rate limit check
        if not rate_limiter.allow(ip):
            log_event(f"Rate limit exceeded: {ip}")
            conn.send(build_response("error", "rate limit exceeded").encode())
            return

        # Attack detection
        risk = detector.analyze(ip)
        if risk["risk"] == "HIGH":
            log_event(f"ATTACK detected from {ip}")
            conn.send(build_response("error", "suspicious activity detected").encode())
            return

        # Parse request
        try:
            packet = json.loads(raw)
        except:
            conn.send(build_response("error", "invalid json").encode())
            return

        # AUTH check
        if packet.get("auth"):
            auth = packet["auth"]
            if not verify(auth.get("user"), auth.get("password")):
                conn.send(build_response("error", "auth failed").encode())
                return

        command = packet.get("command")

        # Commands
        if command == "ping":
            sync.heartbeat(ip)
            response = build_response("ok", "pong", {"ip": ip})

        elif command == "register":
            node_id = packet.get("node_id", ip)
            nodes[node_id] = {"ip": ip, "status": "online"}
            sync.register(node_id)

            log_event(f"Node registered: {node_id}")
            response = build_response("ok", "registered", nodes[node_id])

        elif command == "status":
            response = build_response("ok", "server status", {
                "nodes": len(nodes),
                "online": len(sync.nodes)
            })

        else:
            response = build_response("error", "unknown command")

        conn.send(response.encode())

    except Exception as e:
        log_event(f"Error: {str(e)}")
    finally:
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(100)

    log_event(f"Security Server started on {HOST}:{PORT}")
    print(f"[+] Security Server running on {PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()


if __name__ == "__main__":
    start_server()