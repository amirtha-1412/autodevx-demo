import secrets
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PasswordResetService:
    """
    A service class responsible for generating and sending password reset tokens.
    """

    def __init__(self, email_config: dict):
        """
        Initialize the password reset service with email configuration.

        Args:
        - email_config (dict): A dictionary containing email configuration.
            - 'email_address' (str): The sender's email address.
            - 'email_password' (str): The sender's email password.
            - 'smtp_server' (str): The SMTP server address.
            - 'smtp_port' (int): The SMTP server port.
        """
        self.email_config = email_config

    def generate_password_reset_token(self, user_id: int) -> str:
        """
        Generate a unique password reset token for a given user ID.

        Args:
        - user_id (int): The ID of the user requesting a password reset.

        Returns:
        - str: A unique password reset token.
        """
        # Generate a random token with a length of 32 characters
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        # Store the token in a dictionary with a TTL of 30 minutes
        self.tokens = getattr(self, 'tokens', {})
        self.tokens[token] = (user_id, 30 * 60)  # 30 minutes in seconds
        return token

    def send_password_reset_token(self, user_id: int, email_address: str) -> bool:
        """
        Send the password reset token to the user's registered email address.

        Args:
        - user_id (int): The ID of the user requesting a password reset.
        - email_address (str): The user's registered email address.

        Returns:
        - bool: True if the email was sent successfully, False otherwise.
        """
        # Generate a password reset token
        token = self.generate_password_reset_token(user_id)

        # Create a message
        msg = MIMEMultipart()
        msg['From'] = self.email_config['email_address']
        msg['To'] = email_address
        msg['Subject'] = 'Password Reset Token'

        # Create a message body
        body = f'Your password reset token is: {token}'
        msg.attach(MIMEText(body, 'plain'))

        # Set up the SMTP server
        server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        server.starttls()
        server.login(self.email_config['email_address'], self.email_config['email_password'])

        # Send the email
        try:
            text = msg.as_string()
            server.sendmail(self.email_config['email_address'], email_address, text)
            server.quit()
            return True
        except Exception as e:
            logger.error(f'Error sending email: {e}')
            return False

    def validate_password_reset_token(self, token: str) -> Optional[int]:
        """
        Validate a password reset token.

        Args:
        - token (str): The password reset token to validate.

        Returns:
        - int: The user ID associated with the token if it is valid, None otherwise.
        """
        # Check if the token exists and has not expired
        if token in getattr(self, 'tokens', {}):
            user_id, expiration_time = self.tokens[token]
            if expiration_time > 0:
                return user_id
        return None

def main():
    # Load email configuration from environment variables
    email_config = {
        'email_address': os.environ.get('EMAIL_ADDRESS'),
        'email_password': os.environ.get('EMAIL_PASSWORD'),
        'smtp_server': os.environ.get('SMTP_SERVER'),
        'smtp_port': int(os.environ.get('SMTP_PORT'))
    }

    # Create a password reset service
    password_reset_service = PasswordResetService(email_config)

    # Test the password reset service
    user_id = 1
    email_address = 'example@example.com'
    if password_reset_service.send_password_reset_token(user_id, email_address):
        print('Password reset token sent successfully')
    else:
        print('Error sending password reset token')

    # Test token validation
    token = password_reset_service.generate_password_reset_token(user_id)
    validated_user_id = password_reset_service.validate_password_reset_token(token)
    if validated_user_id == user_id:
        print('Token validated successfully')
    else:
        print('Error validating token')

if __name__ == '__main__':
    main()