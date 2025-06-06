import smtplib
from email.message import EmailMessage
import random
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
import uuid

def send_verification_email(to_email, token):
    link = f"http://localhost:5000/verify?token={token}"
    msg = EmailMessage()
    msg['Subject'] = "Home Task - Verify your email"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f"""
Hi,

Thank you for registering!

Please verify your email by clicking the link below:
{link}

If you did not request this, you can safely ignore this email.
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


def generate_verification_code():
    return str(uuid.uuid4())