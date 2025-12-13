from flask import Flask, render_template, request, redirect, session
from users import register_user, login_user

app = Flask(__name__)
app.secret_key = "tamanna-secret-key"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if login_user(request.form["username"], request.form["password"]):
            session["user"] = request.form["username"]
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        register_user(request.form["username"], request.form["password"])
        return redirect("/")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", user=session["user"])

app.run(debug=True)