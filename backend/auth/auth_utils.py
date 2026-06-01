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
# JWT Token Generation
# ─────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """
    Generate a JWT access token.
    
    Args:
        data: Payload data for the token
        expires_delta: Token expiration time
    
    Returns:
        JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        to_encode["exp"] = datetime.utcnow() + expires_delta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ─────────────────────────────────────────────
# JWT Token Validation
# ─────────────────────────────────────────────

def decode_access_token(token: str) -> dict:
    """
    Decode a JWT access token.
    
    Args:
        token: JWT access token
    
    Returns:
        Decoded token payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload