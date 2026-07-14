import socket


def check_port(host, port):
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        return True
    except:
        return False
