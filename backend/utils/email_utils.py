import smtplib
from email.message import EmailMessage
import random
from config import EMAIL_ADDRESS, EMAIL_PASSWORD

def send_verification_email(to_email, code):
    msg = EmailMessage()
    msg['Subject'] = "Home Task - Verify your email"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f"Hi, your verification code for completing the registration is: {code}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def generate_verification_code():
    return str(random.randint(100000, 999999))  # Generates a 6-digit code