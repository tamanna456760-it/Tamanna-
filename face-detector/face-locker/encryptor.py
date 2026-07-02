from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    return open(KEY_FILE, "rb").read()

def encrypt_file(file_path):
    key = load_key()
    f = Fernet(key)

    with open(file_path, "rb") as file:
        data = file.read()

    encrypted = f.encrypt(data)

    with open(file_path + ".enc", "wb") as file:
        file.write(encrypted)

    os.remove(file_path)

def decrypt_file(file_path):
    key = load_key()
    f = Fernet(key)

    with open(file_path, "rb") as file:
        encrypted = file.read()

    decrypted = f.decrypt(encrypted)

    output = file_path.replace(".enc", "")

    with open(output, "wb") as file:
        file.write(decrypted)

    os.remove(file_path)