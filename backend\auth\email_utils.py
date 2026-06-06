"""
backend/auth/email_utils.py
---------------------------------------------
Email Utilities - Send emails to users
Provides a way to send emails to users.

Features:
  - Send emails using a SMTP server
"""

import smtplib
from email.mime.text import MIMEText
from typing import Optional

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-username")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-password")


def send_email(to: str, subject: str, body: str):
    """
    Send an email to the user.

    Args:
        to: The user's email address
        subject: The email subject
        body: The email body
    """
    # Create a text message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USERNAME
    msg["To"] = to

    # Send the email
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(SMTP_USERNAME, to, msg.as_string())
    server.quit()