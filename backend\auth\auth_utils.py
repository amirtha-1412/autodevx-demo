"""
backend/auth/auth_utils.py
---------------------------------------------
Authentication Utilities - JWT & Password Hashing
Provides secure authentication with JWT tokens.

Features:
  - Password hashing with bcrypt
  - JWT token generation and validation
  - Token expiration handling
  - Secure password verification
  - Password reset functionality
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import os
from backend.auth.email_utils import send_email

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ─────────────────────────────────────────────
# Password Hashing
# ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    # Convert password to bytes and hash
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
    
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ─────────────────────────────────────────────
# JWT Token Generation and Validation
# ─────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create an access token for the user.

    Args:
        data: The data to encode in the token
        expires_delta: The expiration time for the token

    Returns:
        The access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """
    Decode an access token.

    Args:
        token: The access token to decode

    Returns:
        The decoded data
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─────────────────────────────────────────────
# Password Reset
# ─────────────────────────────────────────────

def send_password_reset_email(email: str):
    """
    Send a password reset email to the user.

    Args:
        email: The user's email address
    """
    # Generate a password reset token
    token = create_access_token({"email": email}, expires_delta=timedelta(minutes=30))
    # Send the email
    send_email(email, "Password Reset", f"Reset your password: {token}")


def reset_password(token: str, new_password: str):
    """
    Reset the user's password.

    Args:
        token: The password reset token
        new_password: The new password
    """
    try:
        # Decode the token
        payload = decode_access_token(token)
        email = payload["email"]
        # Update the user's password
        user = get_user(email)
        if user:
            user.hashed_password = hash_password(new_password)
            # Save the changes
            # ...
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )