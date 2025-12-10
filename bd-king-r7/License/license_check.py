def check_license(code):
    if code.startswith("BD-KING-R7-") and len(code) == 18:
        return "✔ Valid format"
    return "❌ Invalid license format"

user_code = input("Enter your BD-KING-R7 License: ")
print(check_license(user_code))