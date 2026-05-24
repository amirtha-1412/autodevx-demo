from password_reset_service import PasswordResetService

class UserService:
    """
    Service responsible for user-related operations, including password resets.
    """

    def __init__(self, password_reset_service: PasswordResetService):
        """
        Initializes the user service with a password reset service instance.

        Args:
        - password_reset_service (PasswordResetService): The password reset service instance.
        """
        self.password_reset_service = password_reset_service
        self.users = {}  # For demonstration purposes, we'll use a simple dictionary

    def request_password_reset(self, user_id: int, user_email: str) -> bool:
        """
        Requests a password reset for the given user ID and email.

        Args:
        - user_id (int): The ID of the user requesting a password reset.
        - user_email (str): The email address of the user.

        Returns:
        - bool: True if the password reset request was successful, False otherwise.
        """
        token = self.password_reset_service.generate_password_reset_token(user_id)
        return self.password_reset_service.send_password_reset_email(user_email, token)

    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Resets the password for the user associated with the given token.

        Args:
        - token (str): The password reset token.
        - new_password (str): The new password.

        Returns:
        - bool: True if the password was reset successfully, False otherwise.
        """
        user_id = self.password_reset_service.validate_password_reset_token(token)
        if user_id:
            # Update the user's password in the database or cache
            # For demonstration purposes, we'll use a simple dictionary
            self.users[user_id] = {'password': new_password}
            return True
        return False