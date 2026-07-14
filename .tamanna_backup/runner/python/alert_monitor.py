# alert_monitor.py
import smtplib
from email.message import EmailMessage


def send_alert(message):
    email = EmailMessage()
    email.set_content(message)
    email["Subject"] = "Tamanna System Alert"
    email["From"] = "your_email@gmail.com"
    email["To"] = "tamanna456760@gmail.com"

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login("your_email@gmail.com", "password")  # Use app password
        smtp.send_message(email)


# Example alert
send_alert("Device 192.168.1.15 is offline!")
