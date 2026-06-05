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
  - Password reset token generation and validation
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import os
import secrets

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password reset token configuration
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 30

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


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create an access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
    
    Returns:
        Access token
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
        token: Access token to decode
    
    Returns:
        Decoded token data
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def generate_password_reset_token(user: str) -> str:
    """
    Generate a password reset token.
    
    Args:
        user: User to generate token for
    
    Returns:
        Password reset token
    """
    token = secrets.token_urlsafe(16)
    # Store the token in the database with the user
    return token


def validate_password_reset_token(token: str) -> Optional[str]:
    """
    Validate a password reset token.
    
    Args:
        token: Token to validate
    
    Returns:
        User if token is valid, None otherwise
    """
    # Check the token in the database
    # If valid, return the user
    # If not, return None
    pass