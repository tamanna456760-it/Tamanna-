import hashlib

USERS = {"admin": hashlib.sha256(b"password").hexdigest()}


def verify(username, password):
    digest = hashlib.sha256(password.encode()).hexdigest()

    return USERS.get(username) == digest
