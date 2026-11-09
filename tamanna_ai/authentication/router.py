"""Tamanna AI account authentication: SQLite + PBKDF2 + signed HttpOnly sessions."""
import base64, hashlib, hmac, json, os, re, secrets, sqlite3, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Cookie, HTTPException, Request, Response
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/auth", tags=["authentication"])
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)
DB = Path(os.getenv("TAMANNA_AUTH_DB", str(DATA / "accounts.sqlite3")))
COOKIE = "tamanna_session"
LIFETIME = max(900, int(os.getenv("TAMANNA_SESSION_SECONDS", "604800")))
COOKIE_SECURE = os.getenv("TAMANNA_COOKIE_SECURE", "1").lower() not in ("0", "false", "no")
ROUNDS = 310000
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def now():
    return datetime.now(timezone.utc).isoformat()

def db():
    c = sqlite3.connect(str(DB), timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    with db() as c:
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("""CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT NOT NULL UNIQUE COLLATE NOCASE,
          name TEXT NOT NULL,password_hash TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS preferences(
          user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
          data TEXT NOT NULL DEFAULT '{}',updated_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS sessions(
          token_hash TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          expires INTEGER NOT NULL,created_at TEXT NOT NULL)""")
        c.execute("CREATE INDEX IF NOT EXISTS sessions_user_idx ON sessions(user_id)")
        c.execute("""CREATE TABLE IF NOT EXISTS auth_attempts(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ip_hash TEXT NOT NULL, action TEXT NOT NULL, attempted_at INTEGER NOT NULL)""")
        c.execute("CREATE INDEX IF NOT EXISTS auth_attempts_lookup_idx ON auth_attempts(ip_hash,action,attempted_at)")

def secret():
    value = os.getenv("TAMANNA_SESSION_SECRET", "").strip()
    if len(value) < 32:
        raise RuntimeError("Set TAMANNA_SESSION_SECRET to a random secret of at least 32 characters.")
    return value.encode()

def password_hash(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ROUNDS)
    return "pbkdf2$" + str(ROUNDS) + "$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()

def password_ok(password, stored):
    try:
        algo, rounds, salt, digest = stored.split("$", 3)
        if algo != "pbkdf2": return False
        iterations = int(rounds)
        if not 100000 <= iterations <= 1000000:
            return False
        decoded_salt = base64.urlsafe_b64decode(salt)
        if len(decoded_salt) != 16:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), decoded_salt, iterations)
        return hmac.compare_digest(actual, base64.urlsafe_b64decode(digest))
    except (ValueError, TypeError): return False

# Perform equivalent PBKDF2 work for unknown accounts to reduce email enumeration.
_DUMMY_PASSWORD_HASH = password_hash("tamanna-invalid-account-dummy-password")


def sign(payload):
    return base64.urlsafe_b64encode(hmac.new(secret(), payload.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()

def issue_session(user_id):
    expiry = int(time.time()) + LIFETIME
    payload = "{}.{}.{}".format(user_id, expiry, secrets.token_urlsafe(24))
    token = payload + "." + sign(payload)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with db() as c:
        c.execute("DELETE FROM sessions WHERE expires < ?", (int(time.time()),))
        c.execute("INSERT INTO sessions VALUES(?,?,?,?)", (token_hash, user_id, expiry, now()))
    return token

def current_user(token):
    if not token: return None
    try:
        uid, expiry, nonce, signature = token.split(".", 3)
        payload = "{}.{}.{}".format(uid, expiry, nonce)
        if not hmac.compare_digest(signature, sign(payload)) or int(expiry) <= int(time.time()): return None
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with db() as c:
            row = c.execute("""SELECT u.id,u.email,u.name,u.created_at FROM sessions s
              JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires>?""",
              (token_hash, int(time.time()))).fetchone()
        return dict(row) if row else None
    except (ValueError, TypeError): return None

def require_user(token):
    user = current_user(token)
    if not user: raise HTTPException(401, "Please sign in.")
    return user

def rate_limit_auth(request, action):
    """Persistent per-IP throttle for signup/login attempts (10 per 15 minutes)."""
    host = request.client.host if request.client else "unknown"
    try:
        session_secret = secret()
    except RuntimeError as exc:
        raise HTTPException(
            503,
            "Authentication is not configured. Set TAMANNA_SESSION_SECRET in the private .env file.",
        ) from exc
    ip_hash = hmac.new(session_secret, host.encode("utf-8"), hashlib.sha256).hexdigest()
    current = int(time.time())
    window_start = current - 900
    with db() as c:
        c.execute("BEGIN IMMEDIATE")
        c.execute("DELETE FROM auth_attempts WHERE attempted_at < ?", (current - 3600,))
        count = c.execute(
            "SELECT COUNT(*) FROM auth_attempts WHERE ip_hash=? AND action=? AND attempted_at>=?",
            (ip_hash, action, window_start),
        ).fetchone()[0]
        if count >= 10:
            raise HTTPException(429, "Too many authentication attempts. Try again in 15 minutes.")
        c.execute(
            "INSERT INTO auth_attempts(ip_hash,action,attempted_at) VALUES(?,?,?)",
            (ip_hash, action, current),
        )


def check_origin(request):
    # Fetch Metadata protects cookie-authenticated mutations when a browser
    # omits Origin but explicitly identifies the request as cross-site.
    fetch_site = request.headers.get("sec-fetch-site", "").strip().lower()
    origin = request.headers.get("origin")
    # Same-site is not necessarily same-origin: a hostile sibling subdomain
    # can still cause cookie-authenticated requests. Require an explicit
    # allowlisted Origin whenever the browser reports same-site without one.
    if fetch_site == "cross-site" or (fetch_site == "same-site" and not origin):
        raise HTTPException(403, "Unverified cross-origin browser requests are not allowed.")
    if origin:
        allowed = [x.strip().rstrip("/") for x in os.getenv("TAMANNA_CORS_ORIGINS",
          "https://www.bd-king-r7.com").split(",") if x.strip()]
        if origin.rstrip("/") not in allowed: raise HTTPException(403, "Untrusted request origin.")

def set_cookie(response, token):
    response.set_cookie(COOKIE, token, max_age=LIFETIME, httponly=True,
      secure=COOKIE_SECURE, samesite="lax", path="/")

class Signup(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=12, max_length=128)
class Login(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)
class Profile(BaseModel):
    name: str = Field(min_length=2, max_length=80)
class ChangePassword(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)
class Preferences(BaseModel):
    preferences: dict = Field(default_factory=dict)

@router.on_event("startup")
def startup():
    init_db()

@router.post("/signup", status_code=201)
def signup(data: Signup, request: Request, response: Response):
    check_origin(request)
    rate_limit_auth(request, "signup")
    email, name = data.email.strip().lower(), data.name.strip()
    if not EMAIL_RE.fullmatch(email): raise HTTPException(422, "Enter a valid email address.")
    if len(name) < 2: raise HTTPException(422, "Name must contain at least 2 non-whitespace characters.")
    try:
        with db() as c:
            cur = c.execute("INSERT INTO users(email,name,password_hash,created_at,updated_at) VALUES(?,?,?,?,?)",
              (email, name, password_hash(data.password), now(), now()))
            uid = cur.lastrowid
            c.execute("INSERT INTO preferences(user_id,data,updated_at) VALUES(?,?,?)", (uid, "{}", now()))
    except sqlite3.IntegrityError: raise HTTPException(409, "An account with this email already exists.")
    set_cookie(response, issue_session(uid))
    return {"ok": True, "user": {"id": uid, "email": email, "name": name}}

@router.post("/login")
def login(data: Login, request: Request, response: Response):
    check_origin(request)
    rate_limit_auth(request, "login")
    with db() as c:
        row = c.execute("SELECT * FROM users WHERE email=? COLLATE NOCASE", (data.email.strip().lower(),)).fetchone()
    stored_hash = row["password_hash"] if row else _DUMMY_PASSWORD_HASH
    password_matches = password_ok(data.password, stored_hash)
    if not row or not password_matches:
        raise HTTPException(401, "Email or password is incorrect.")
    set_cookie(response, issue_session(row["id"]))
    return {"ok": True, "user": {"id": row["id"], "email": row["email"], "name": row["name"]}}

@router.get("/me")
def me(token: Optional[str] = Cookie(default=None, alias=COOKIE)):
    return {"ok": True, "user": require_user(token)}

@router.post("/logout")
def logout(request: Request, response: Response, token: Optional[str] = Cookie(default=None, alias=COOKIE)):
    check_origin(request)
    if token:
        with db() as c:
            c.execute("DELETE FROM sessions WHERE token_hash=?", (hashlib.sha256(token.encode()).hexdigest(),))
    response.delete_cookie(COOKIE, path="/", httponly=True, secure=COOKIE_SECURE, samesite="lax")
    return {"ok": True}

@router.patch("/profile")
def update_profile(data: Profile, request: Request, token: Optional[str] = Cookie(default=None, alias=COOKIE)):
    check_origin(request)
    user = require_user(token)
    name = data.name.strip()
    if len(name) < 2: raise HTTPException(422, "Name must contain at least 2 characters.")
    with db() as c: c.execute("UPDATE users SET name=?,updated_at=? WHERE id=?", (name, now(), user["id"]))
    return {"ok": True, "name": name}

@router.post("/change-password")
def change_password(data: ChangePassword, request: Request, token: Optional[str] = Cookie(default=None, alias=COOKIE)):
    check_origin(request)
    user = require_user(token)
    with db() as c:
        row = c.execute("SELECT password_hash FROM users WHERE id=?", (user["id"],)).fetchone()
        if not row or not password_ok(data.current_password, row["password_hash"]):
            raise HTTPException(400, "Current password is incorrect.")
        c.execute("UPDATE users SET password_hash=?,updated_at=? WHERE id=?", (password_hash(data.new_password), now(), user["id"]))
        c.execute("DELETE FROM sessions WHERE user_id=?", (user["id"],))
    return {"ok": True, "message": "Password updated. Sign in again."}

@router.get("/preferences")
def get_preferences(token: Optional[str] = Cookie(default=None, alias=COOKIE)):
    user = require_user(token)
    with db() as c: row = c.execute("SELECT data FROM preferences WHERE user_id=?", (user["id"],)).fetchone()
    try: value = json.loads(row["data"]) if row else {}
    except (ValueError, TypeError): value = {}
    return {"ok": True, "preferences": value}

@router.put("/preferences")
def put_preferences(data: Preferences, request: Request, token: Optional[str] = Cookie(default=None, alias=COOKIE)):
    check_origin(request)
    user = require_user(token)
    if len(json.dumps(data.preferences, ensure_ascii=False)) > 12000:
        raise HTTPException(413, "Preferences payload is too large.")
    allowed = {"theme", "accent", "language", "fontSize", "chatHistory", "notifications", "compactMode"}
    clean = {k: v for k, v in data.preferences.items() if k in allowed}
    with db() as c:
        c.execute("""INSERT INTO preferences(user_id,data,updated_at) VALUES(?,?,?)
          ON CONFLICT(user_id) DO UPDATE SET data=excluded.data,updated_at=excluded.updated_at""",
          (user["id"], json.dumps(clean, ensure_ascii=False), now()))
    return {"ok": True, "preferences": clean}
