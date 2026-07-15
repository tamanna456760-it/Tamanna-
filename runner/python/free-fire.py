import json
import os

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------- Database ----------
DB_FILE = "data.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_data()

# ---------- App ----------
app = ctk.CTk()
app.geometry("400x500")
app.title("🔥 Pro Panel System")

# ---------- Frames ----------
login_frame = ctk.CTkFrame(app)
main_frame = ctk.CTkFrame(app)

login_frame.pack(fill="both", expand=True)

# ---------- Login ----------
def login():
    user = username.get()
    pwd = password.get()

    if user in db and db[user]["password"] == pwd:
        open_main(user)
    else:
        output_login.configure(text="❌ Login Failed")

def register():
    user = username.get()
    pwd = password.get()

    if user in db:
        output_login.configure(text="⚠️ User Exists")
        return

    db[user] = {
        "password": pwd,
        "uid": "6642083257",
        "bundles": []
    }
    save_data(db)
    output_login.configure(text="✅ Registered")

username = ctk.CTkEntry(login_frame, placeholder_text="Username")
username.pack(pady=10)

password = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*")
password.pack(pady=10)

ctk.CTkButton(login_frame, text="Login", command=login).pack(pady=5)
ctk.CTkButton(login_frame, text="Register", command=register).pack(pady=5)

output_login = ctk.CTkLabel(login_frame, text="")
output_login.pack(pady=10)

# ---------- Main Panel ----------
def open_main(user):
    login_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

    user_data = db[user]

    uid_label.configure(text=f"UID: {user_data['uid']}")
    show_bundles(user)

current_user = None

def show_bundles(user):
    bundle_box.delete("1.0", "end")
    bundles = db[user]["bundles"]
    if not bundles:
        bundle_box.insert("end", "No Bundles\n")
    else:
        for b in bundles:
            bundle_box.insert("end", f"{b}\n")

def unlock_bundle():
    bundle = bundle_entry.get()
    if bundle == "":
        return

    db[current_user]["bundles"].append(bundle)
    save_data(db)

    show_bundles(current_user)

def set_user(user):
    global current_user
    current_user = user

# ---------- Main UI ----------
uid_label = ctk.CTkLabel(main_frame, text="UID:")
uid_label.pack(pady=10)

bundle_box = ctk.CTkTextbox(main_frame, width=300, height=200)
bundle_box.pack(pady=10)

bundle_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter Bundle Name")
bundle_entry.pack(pady=5)

def unlock_click():
    unlock_bundle()

ctk.CTkButton(main_frame, text="Unlock Bundle", command=unlock_click).pack(pady=5)

def logout():
    main_frame.pack_forget()
    login_frame.pack(fill="both", expand=True)

ctk.CTkButton(main_frame, text="Logout", command=logout).pack(pady=10)

# Fix user setting
def open_main(user):
    global current_user
    current_user = user

    login_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

    uid_label.configure(text=f"UID: {db[user]['uid']}")
    show_bundles(user)

app.mainloop()