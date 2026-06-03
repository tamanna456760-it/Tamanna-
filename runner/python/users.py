from werkzeug.security import generate_password_hash, check_password_hash

users_db = {}

def register_user(username, password):
    if username in users_db:
        return False
    users_db[username] = generate_password_hash(password)
    return True

def login_user(username, password):
    if username in users_db and check_password_hash(users_db[username], password):
        return True
    return False