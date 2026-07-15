import smtplib
from datetime import datetime
from email.mime.text import MIMEText

# ====== USER INFO ======
name = "HM Insan Ali"
my_number = "01856992843"
suspicious_number = "+880078678"

# ====== EMAIL SETUP ======
sender_email = "tamanna456760@gmail.com"
sender_password = "insan_tamanna00@@##"  # Gmail App Password লাগবে
receiver_email = ["care@robi.com.bd", "complaint@btrc.gov.bd"]

subject = "URGENT: Cyber Security Complaint"

body = f"""
Dear Sir/Madam,

I am writing to report a serious cyber security concern.

Name: {name}
Mobile Number: {my_number}
Location: Dubai (Probashi)
Suspicious Number: {suspicious_number}

I request immediate investigation and necessary action.

Date: {datetime.now()}

Sincerely,
{name}
"""

msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = sender_email
msg["To"] = ", ".join(receiver_email)

# ====== SEND EMAIL ======
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(sender_email, sender_password)
server.sendmail(sender_email, receiver_email, msg.as_string())
server.quit()

print("Email Sent Successfully")