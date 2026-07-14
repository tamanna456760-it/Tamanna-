from flask import Blueprint, request, jsonify
from users import register_user, login_user

api = Blueprint("api", __name__)


@api.route("/register", methods=["POST"])
def api_register():
    data = request.json
    if register_user(data["username"], data["password"]):
        return jsonify({"status": "registered"})
    return jsonify({"error": "user exists"}), 400


@api.route("/login", methods=["POST"])
def api_login():
    data = request.json
    if login_user(data["username"], data["password"]):
        return jsonify({"status": "login success"})
    return jsonify({"error": "invalid credentials"}), 401
