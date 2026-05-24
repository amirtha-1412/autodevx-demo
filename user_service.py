from typing import Dict

class UserService:
    """
    A service for managing user data.
    """

    def __init__(self):
        """
        Initializes the UserService.
        """
        # Use a secure dictionary to store user data
        self.users: Dict[str, Dict[str, str]] = {}

    def get_user_email(self, user_id: str) -> str:
        """
        Gets the email address for the given user ID.

        Args:
        - user_id (str): The ID of the user.

        Returns:
        - str: The email address of the user.
        """
        if user_id in self.users:
            return self.users[user_id]['email']
        else:
            raise ValueError("User not found")

    def add_user(self, user_id: str, email: str) -> None:
        """
        Adds a new user to the system.

        Args:
        - user_id (str): The ID of the user.
        - email (str): The email address of the user.
        """
        if user_id and email:
            self.users[user_id] = {'email': email}
        else:
            raise ValueError("User ID and email address are required")