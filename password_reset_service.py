import secrets
import string
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from typing import Optional

class PasswordResetService:
    """
    Service responsible for generating password reset tokens and sending them to users via email.
    """

    def __init__(self, smtp_server: str, smtp_port: int, from_email: str, password: str):
        """
        Initializes the password reset service with SMTP server details.

        Args:
        - smtp_server (str): The SMTP server to use for sending emails.
        - smtp_port (int): The port number of the SMTP server.
        - from_email (str): The email address to use as the sender.
        - password (str): The password for the sender email account.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.password = password
        self.token_expiration_time = timedelta(minutes=30)  # 30 minutes

    def generate_password_reset_token(self, user_id: int) -> str:
        """
        Generates a unique password reset token for the given user ID.

        Args:
        - user_id (int): The ID of the user requesting a password reset.

        Returns:
        - str: A unique password reset token.
        """
        token = secrets.token_urlsafe(16)
        # Store the token in a database or cache with the user ID and expiration time
        # For demonstration purposes, we'll use a simple dictionary
        self.tokens = getattr(self, 'tokens', {})
        self.tokens[token] = {'user_id': user_id, 'expiration_time': datetime.now() + self.token_expiration_time}
        return token

    def send_password_reset_email(self, user_email: str, token: str) -> bool:
        """
        Sends a password reset email to the user with the given token.

        Args:
        - user_email (str): The email address of the user.
        - token (str): The password reset token.

        Returns:
        - bool: True if the email was sent successfully, False otherwise.
        """
        try:
            msg = EmailMessage()
            msg.set_content(f"Password reset token: {token}")
            msg['Subject'] = "Password Reset Request"
            msg['From'] = self.from_email
            msg['To'] = user_email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(self.from_email, self.password)
                smtp.send_message(msg)
            return True
        except smtplib.SMTPException as e:
            print(f"Error sending email: {e}")
            return False

    def validate_password_reset_token(self, token: str) -> Optional[int]:
        """
        Validates the given password reset token and returns the associated user ID if valid.

        Args:
        - token (str): The password reset token to validate.

        Returns:
        - Optional[int]: The user ID associated with the token if valid, None otherwise.
        """
        if token in self.tokens:
            token_info = self.tokens[token]
            if datetime.now() < token_info['expiration_time']:
                return token_info['user_id']
        return None