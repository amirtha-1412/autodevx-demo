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
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import os

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
    Create an access token with the provided data.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        str: Access token
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
        token: Access token

    Returns:
        dict: Decoded token data
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
# User Authentication
# ─────────────────────────────────────────────

def authenticate_user(username: str, password: str):
    """
    Authenticate a user with the provided username and password.

    Args:
        username: Username
        password: Password

    Returns:
        UserInDB: Authenticated user
    """
    # Replace with your actual user authentication logic
    # For demonstration purposes, assume a user with the provided username and password exists
    user = UserInDB(
        username=username,
        email="user@example.com",
        full_name="John Doe",
        role="admin",
        disabled=False,
        hashed_password=hash_password(password)
    )
    return user


def get_user(username: str):
    """
    Get a user by their username.

    Args:
        username: Username

    Returns:
        UserInDB: User
    """
    # Replace with your actual user retrieval logic
    # For demonstration purposes, assume a user with the provided username exists
    user = UserInDB(
        username=username,
        email="user@example.com",
        full_name="John Doe",
        role="admin",
        disabled=False,
        hashed_password=hash_password("password")
    )
    return user