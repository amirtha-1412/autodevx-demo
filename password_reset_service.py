import secrets
import string
import smtplib
from email.message import EmailMessage
from typing import Dict

class PasswordResetService:
    """
    A service for generating and sending password reset tokens.
    """

    def __init__(self, smtp_server: str, smtp_port: int, from_email: str, password: str):
        """
        Initializes the PasswordResetService.

        Args:
        - smtp_server (str): The SMTP server to use for sending emails.
        - smtp_port (int): The port to use for the SMTP server.
        - from_email (str): The email address to use as the sender.
        - password (str): The password for the sender email account.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.password = password

    def generate_password_reset_token(self, user_id: str) -> str:
        """
        Generates a unique password reset token for the given user ID.

        Args:
        - user_id (str): The ID of the user requesting a password reset.

        Returns:
        - str: A unique password reset token.
        """
        # Generate a random token with a mix of uppercase, lowercase, and digits
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        return token

    def send_password_reset_token(self, user_email: str, token: str) -> None:
        """
        Sends the password reset token to the user's registered email address.

        Args:
        - user_email (str): The email address of the user requesting a password reset.
        - token (str): The password reset token to send.

        Raises:
        - smtplib.SMTPException: If there is an issue connecting to the SMTP server.
        """
        try:
            # Create an email message
            msg = EmailMessage()
            msg.set_content(f"Your password reset token is: {token}")
            msg['Subject'] = "Password Reset Token"
            msg['From'] = self.from_email
            msg['To'] = user_email

            # Send the email using the SMTP server
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
                smtp.login(self.from_email, self.password)
                smtp.send_message(msg)
        except smtplib.SMTPException as e:
            # Handle SMTP server connection issues
            print(f"Error sending email: {e}")

    def request_password_reset(self, user_id: str, user_email: str) -> None:
        """
        Requests a password reset for the given user ID and sends the token to the user's email address.

        Args:
        - user_id (str): The ID of the user requesting a password reset.
        - user_email (str): The email address of the user requesting a password reset.

        Raises:
        - ValueError: If the user ID or email address is invalid.
        """
        if not user_id or not user_email:
            raise ValueError("User ID and email address are required")

        # Generate a password reset token
        token = self.generate_password_reset_token(user_id)

        # Send the token to the user's email address
        self.send_password_reset_token(user_email, token)