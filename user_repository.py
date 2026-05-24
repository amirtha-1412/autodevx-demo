import sqlite3
from email_validator import EmailValidator
from password_validator import PasswordValidator
from typing import Optional

class UserRepository:
    """
    Manages user data in a SQLite database.

    Attributes:
    db_connection (sqlite3.Connection): The connection to the SQLite database.
    """

    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initializes the UserRepository with a database connection.

        Args:
        db_connection (sqlite3.Connection): The connection to the SQLite database.
        """
        self.db_connection = db_connection

    def get_stored_hash(self, email: str) -> Optional[str]:
        """
        Retrieves the stored password hash for a given email address.

        Args:
        email (str): The email address to retrieve the stored hash for.

        Returns:
        Optional[str]: The stored password hash if found, None otherwise.
        """
        # Query the database for the stored hash
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

    def validate_credentials(self, email: str, password: str) -> bool:
        """
        Validates the credentials (email and password) against the stored data.

        Args:
        email (str): The email address to validate.
        password (str): The password to validate.

        Returns:
        bool: True if the credentials are valid, False otherwise.
        """
        # Validate the email format
        email_validator = EmailValidator(email)
        if not email_validator.validate():
            return False

        # Retrieve the stored hash
        stored_hash = self.get_stored_hash(email)
        if not stored_hash:
            return False

        # Validate the password
        password_validator = PasswordValidator(password, stored_hash)
        return password_validator.validate()

    def get_error_message(self, email: str, password: str) -> Optional[str]:
        """
        Returns an error message if the credentials are invalid.

        Args:
        email (str): The email address to validate.
        password (str): The password to validate.

        Returns:
        Optional[str]: An error message if the credentials are invalid, None otherwise.
        """
        # Validate the email format
        email_validator = EmailValidator(email)
        error_message = email_validator.get_error_message()
        if error_message:
            return error_message

        # Retrieve the stored hash
        stored_hash = self.get_stored_hash(email)
        if not stored_hash:
            return "Email address not found."

        # Validate the password
        password_validator = PasswordValidator(password, stored_hash)
        error_message = password_validator.get_error_message()
        if error_message:
            return error_message

        return None