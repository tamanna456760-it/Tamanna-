from users.user import User

users_db = []

def register(username, email, password):
    user = User(username, email, password)
    users_db.append(user)
    return "User registered successfully"

def login(username, password):
    for user in users_db:
        if user.username == username and user.password == password:
            return f"Login successful: {user.role}"
    return "Invalid username or password"