ROLES = {
    "admin": ["read", "write", "delete"],
    "user": ["read"]
}

def check_permission(role, action):
    return action in ROLES.get(role, [])