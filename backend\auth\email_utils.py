"""
backend/auth/email_utils.py
---------------------------------------------
Email Utilities - Send password reset emails
Provides a function to send password reset emails.
"""

from typing import Optional
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr

def send_password_reset_email(email: EmailStr, token: str):
    """
    Send a password reset email to the user.
    
    Args:
        email: User's email address
        token: Password reset token
    """
    # Configure the email service
    mail = FastMail("your-email-service")
    message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        body=f"Reset your password: {token}",
    )
    # Send the email in the background
    mail.send_message(message, background_tasks=BackgroundTasks())