import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from argon2 import PasswordHasher
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'change_this_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') or 'sqlite:///data.db'
app.config['SESSION_COOKIE_SECURE'] = True       # send cookie only over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True     # prevent JS access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Security headers + HSTS + CSP
csp = {
    'default-src': ["'self'"],
    'script-src': ["'self'"],
    'style-src': ["'self'"],
    # add trusted CDNs explicitly if needed
}
Talisman(app, content_security_policy=csp, force_https=True, strict_transport_security=True)

db = SQLAlchemy(app)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
ph = PasswordHasher()

# Simple user table (example)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(500), nullable=False)
    failed_logins = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

# Secure signup (password hashed with Argon2)
@app.route('/signup', methods=['POST'])
@limiter.limit("5 per minute")  # protect endpoint from abuse
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error":"invalid"}), 400
    # simple validation; use validators library for production
    pw_hash = ph.hash(password)
    user = User(email=email, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({"ok": True}), 201

# Secure login with lockout
from datetime import datetime, timedelta
LOCKOUT_THRESHOLD = 5
LOCKOUT_PERIOD = timedelta(minutes=15)

@app.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error":"invalid"}), 401

    # account lockout check
    if user.locked_until and datetime.utcnow() < user.locked_until:
        return jsonify({"error":"account locked"}), 403

    try:
        ph.verify(user.password_hash, password)
        # success: reset counters
        user.failed_logins = 0
        user.locked_until = None
        db.session.commit()
        session.permanent = True
        session['user_id'] = user.id
        return jsonify({"ok":True})
    except Exception:
        user.failed_logins += 1
        if user.failed_logins >= LOCKOUT_THRESHOLD:
            user.locked_until = datetime.utcnow() + LOCKOUT_PERIOD
        db.session.commit()
        return jsonify({"error":"invalid"}), 401

# Example safe DB query (SQLAlchemy handles parameterization)
@app.route('/profile')
def profile():
    uid = session.get('user_id')
    if not uid: return redirect(url_for('login_page'))
    user = User.query.get(uid)
    return jsonify({"email": user.email})

if __name__ == '__main__':
    # For dev only: in production run behind Gunicorn + reverse proxy
    db.create_all()
    app.run(host='0.0.0.0', port=5000)