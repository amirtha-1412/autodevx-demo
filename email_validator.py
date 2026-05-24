import re
from typing import Optional

class EmailValidator:
    """
    Validates an email address format.

    Attributes:
    email (str): The email address to validate.
    """

    def __init__(self, email: str):
        """
        Initializes the EmailValidator with an email address.

        Args:
        email (str): The email address to validate.
        """
        self.email = email

    def validate(self) -> bool:
        """
        Validates the email address format using a regular expression.

        Returns:
        bool: True if the email address is valid, False otherwise.
        """
        # Regular expression for email validation (RFC 5322)
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_regex, self.email))

    def get_error_message(self) -> Optional[str]:
        """
        Returns an error message if the email address is invalid.

        Returns:
        Optional[str]: An error message if the email address is invalid, None otherwise.
        """
        if not self.validate():
            return "Invalid email address format."
        return None