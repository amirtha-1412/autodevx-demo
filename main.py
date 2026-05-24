import sqlite3
from user_repository import UserRepository
from email_validator import EmailValidator
from password_validator import PasswordValidator

def main():
    # Create a SQLite database connection
    db_connection = sqlite3.connect("users.db")

    # Create a UserRepository instance
    user_repository = UserRepository(db_connection)

    # Create a table for users if it doesn't exist
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    db_connection.commit()

    # Example usage:
    email = "example@example.com"
    password = "password123"

    # Validate the email format
    email_validator = EmailValidator(email)
    if not email_validator.validate():
        print(email_validator.get_error_message())
        return

    # Hash the password
    password_validator = PasswordValidator(password, "")
    hashed_password = password_validator._generate_hash(password)

    # Insert the user into the database
    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
    db_connection.commit()

    # Validate the credentials
    is_valid = user_repository.validate_credentials(email, password)
    if not is_valid:
        print(user_repository.get_error_message(email, password))
    else:
        print("Credentials are valid.")

if __name__ == "__main__":
    main()