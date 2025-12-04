import os

def install():
    print("BD-KING-R7 Installer Running...")
    os.makedirs("logs", exist_ok=True)
    print("System ready!")

if __name__ == "__main__":
    install()