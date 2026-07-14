# Tamanna Communication Engine
import socket


class CommunicationEngine:
    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"[COMM] Listening on {self.host}:{self.port}")
            conn, addr = s.accept()
            with conn:
                print(f"[COMM] Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f"[COMM] Received: {data.decode()}")
                    conn.sendall(b"Tamanna Response")


if __name__ == "__main__":
    CommunicationEngine().start_server()
