from cryptography.fernet import Fernet

key = open("secret.key", "rb").read()
f = Fernet(key)

with open("database/user_face.enc", "rb") as file:
    data = file.read()

decrypted = f.decrypt(data)

with open("database/user_face_decrypted.jpg", "wb") as file:
    file.write(decrypted)

print("Decrypted successfully")
