"""
backend/auth/email_utils.py
---------------------------------------------
Email Utilities - Password Reset Email
Provides secure password reset email functionality.

Features:
  - Send password reset email to user's registered email address.
"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ─────────────────────────────────────────────
# Configuration Loader
# ─────────────────────────────────────────────

def get_email_config() -> dict:
    """
    Loads and validates all required email config from environment variables.
    Raises EnvironmentError if any required key is missing.
    """
    config = {
        "SMTP_SERVER": os.getenv("SMTP_SERVER", ""),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
        "FROM_EMAIL": os.getenv("FROM_EMAIL", ""),
        "PASSWORD": os.getenv("PASSWORD", ""),
    }

    # Validate required fields
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required email environment variables: {missing}\n"
            "Please fill them in your .env file."
        )

    return config


# ─────────────────────────────────────────────
# Email Header Builder
# ─────────────────────────────────────────────

def get_email_headers(subject: str, to_email: str, from_email: str) -> dict:
    """
    Builds email headers for password reset email.
    """
    return {
        "Subject": subject,
        "To": to_email,
        "From": from_email,
    }


# ─────────────────────────────────────────────
# Send Password Reset Email
# ─────────────────────────────────────────────

def send_password_reset_email(to_email: str, token: str):
    """
    Send password reset email to user's registered email address.
    """
    # Load email config
    email_config = get_email_config()

    # Build email headers
    headers = get_email_headers(
        subject="Password Reset Request",
        to_email=to_email,
        from_email=email_config["FROM_EMAIL"],
    )

    # Build email body
    body = f"""
    <p>Dear {to_email},</p>
    <p>You have requested to reset your password. Please click on the following link to reset your password:</p>
    <p><a href="http://localhost:8000/auth/reset-password?token={token}">Reset Password</a></p>
    <p>Best regards,</p>
    <p>Admin</p>
    """

    # Send email
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(email_config["SMTP_SERVER"], email_config["SMTP_PORT"])
        server.starttls()
        server.login(email_config["FROM_EMAIL"], email_config["PASSWORD"])

        # Build email message
        msg = MIMEMultipart()
        msg["Subject"] = headers["Subject"]
        msg["To"] = headers["To"]
        msg["From"] = headers["From"]
        msg.attach(MIMEText(body, "html"))

        # Send email
        server.sendmail(email_config["FROM_EMAIL"], to_email, msg.as_string())

        # Close SMTP connection
        server.quit()
    except Exception as e:
        # Raise error if email sending fails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email",
        )