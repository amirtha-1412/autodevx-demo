from password_reset_service import PasswordResetService
from user_service import UserService

def main():
    # Create a PasswordResetService instance
    password_reset_service = PasswordResetService('smtp.example.com', 465, 'from@example.com', 'password')

    # Create a UserService instance
    user_service = UserService()

    # Add a user to the system
    user_service.add_user('user1', 'user1@example.com')

    # Request a password reset for the user
    try:
        password_reset_service.request_password_reset('user1', user_service.get_user_email('user1'))
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()