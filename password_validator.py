import hashlib
import secrets
from typing import Optional

class PasswordValidator:
    """
    Validates a password against a stored password hash.

    Attributes:
    password (str): The password to validate.
    stored_hash (str): The stored password hash.
    """

    def __init__(self, password: str, stored_hash: str):
        """
        Initializes the PasswordValidator with a password and a stored hash.

        Args:
        password (str): The password to validate.
        stored_hash (str): The stored password hash.
        """
        self.password = password
        self.stored_hash = stored_hash

    def validate(self) -> bool:
        """
        Validates the password against the stored hash.

        Returns:
        bool: True if the password is valid, False otherwise.
        """
        # Generate a hash from the provided password
        password_hash = self._generate_hash(self.password)
        return password_hash == self.stored_hash

    def _generate_hash(self, password: str) -> str:
        """
        Generates a hash from a password using SHA-256 and a random salt.

        Args:
        password (str): The password to hash.

        Returns:
        str: The hashed password.
        """
        # Generate a random salt
        salt = secrets.token_bytes(16)
        # Generate a hash from the password and salt
        hash_object = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        # Return the salt and hash as a single string
        return salt.hex() + ":" + hash_object.hex()

    def get_error_message(self) -> Optional[str]:
        """
        Returns an error message if the password is invalid.

        Returns:
        Optional[str]: An error message if the password is invalid, None otherwise.
        """
        if not self.validate():
            return "Invalid password."
        return None