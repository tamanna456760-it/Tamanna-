class User:
    def __init__(self, username, email, password, role="user"):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def info(self):
        return {"username": self.username, "email": self.email, "role": self.role}
