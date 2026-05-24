"""
backend/email.py
---------------------------------------------
Email Service
Provides email sending functionality.
"""

from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(
    recipient: str,
    subject: str,
    body: str,
    background_tasks: Optional[BackgroundTasks] = None,
):
    """
    Send an email to the recipient.

    Args:
    - recipient (str): The recipient's email address.
    - subject (str): The email subject.
    - body (str): The email body.
    - background_tasks (Optional[BackgroundTasks]): The background tasks.

    Returns:
    - None
    """
    if background_tasks:
        background_tasks.add_task(send_email_async, recipient, subject, body)
    else:
        send_email_async(recipient, subject, body)


def send_email_async(recipient: str, subject: str, body: str):
    """
    Send an email to the recipient asynchronously.

    Args:
    - recipient (str): The recipient's email address.
    - subject (str): The email subject.
    - body (str): The email body.

    Returns:
    - None
    """
    msg = MIMEMultipart()
    msg["From"] = "your-email@gmail.com"
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(msg["From"], "your-password")
    text = msg.as_string()
    server.sendmail(msg["From"], msg["To"], text)
    server.quit()