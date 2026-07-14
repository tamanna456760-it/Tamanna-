# Any_server_protocol.py

import json
import socket
from datetime import datetime


class ServerProtocol:
    def __init__(self):
        self.version = "1.0"
        self.name = "AnyServerProtocol"

    def process(self, data):
        try:
            packet = json.loads(data)

            response = {
                "protocol": self.name,
                "version": self.version,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
                "received": packet,
            }

            return json.dumps(response)

        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})


def start_server(host="0.0.0.0", port=9000):
    protocol = ServerProtocol()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(10)

    print(f"[+] Server listening on {host}:{port}")

    while True:
        client, addr = server.accept()
        print(f"[+] Connection from {addr}")

        try:
            data = client.recv(4096).decode()
            response = protocol.process(data)

            client.send(response.encode())

        except Exception as err:
            print(f"[!] Error: {err}")

        finally:
            client.close()


if __name__ == "__main__":
    start_server()
