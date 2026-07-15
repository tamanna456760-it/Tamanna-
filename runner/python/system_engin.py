# Tamanna System Connection Engine
import platform


def system_info():
    print("[SYSTEM] OS:", platform.system())
    print("[SYSTEM] Version:", platform.version())
    print("[SYSTEM] Machine:", platform.machine())

if __name__ == "__main__":
    system_info()
