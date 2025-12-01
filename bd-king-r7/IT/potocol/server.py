# server.py
import socket
s = socket.socket()
s.bind(("0.0.0.0", 5555))
s.listen(1)
print("Server listening on 5555")
conn, addr = s.accept()
print("Connected:", addr)
conn.sendall(b"hello from phone (no cloud)")
print(conn.recv(1024))
conn.close()

# client.py
import socket
c = socket.socket()
c.connect(("192.168.1.10", 5555))  # replace with server IP on same Wi‑Fi
print(c.recv(1024))
c.sendall(b"client ack")
c.close()
