"""
backend/auth/auth_routes.py
---------------------------------------------
Authentication Routes - Login & Token Management
Provides secure login and token endpoints.

Endpoints:
  POST /auth/login - Login with username/password
  GET /auth/me - Get current user info
  POST /auth/refresh - Refresh access token
  POST /auth/forgot-password - Send password reset email
  POST /auth/reset-password - Reset password with token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta

from backend.auth.auth_utils import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    hash_password,
    verify_password,
)
from backend.jira.auth import get_jira_config

# ─────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int


class User(BaseModel):
    """User model."""
    username: str
    email: str
    full_name: str
    role: str
    disabled: bool = False


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


class PasswordResetRequest(BaseModel):
    """Password reset request model."""
    email: str


class PasswordReset(BaseModel):
    """Password reset model."""
    token: str
    new_password: str


# ─────────────────────────────────────────────
# OAuth2 Configuration
# ─────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ─────────────────────────────────────────────
# Dependency: Get Current User
# ─────────────────────────────────────────────

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user from the access token.

    Args:
        token: Access token

    Returns:
        UserInDB: Current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = {"username": username}
    except JWTError:
        raise credentials_exception
    user = get_user(token_data["username"])
    if user is None:
        raise credentials_exception
    return user


# ─────────────────────────────────────────────
# Forgot Password Endpoint
# ─────────────────────────────────────────────

async def forgot_password(request: PasswordResetRequest):
    """
    Send a password reset email to the user.

    Args:
        request: Password reset request

    Returns:
        dict: Success message
    """
    user = get_user(request.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    # Generate a unique token for password reset
    token = create_access_token(data={"username": user.username}, expires_delta=timedelta(minutes=30))
    # Send the token to the user via email
    jira_config = get_jira_config()
    try:
        # Send email using Jira's email service
        # Replace with your actual email sending logic
        print(f"  [AgentName] Sending password reset email to {user.email}...")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email",
        )
    return {"message": "Password reset email sent successfully"}


# ─────────────────────────────────────────────
# Reset Password Endpoint
# ─────────────────────────────────────────────

async def reset_password(request: PasswordReset):
    """
    Reset the user's password with the provided token.

    Args:
        request: Password reset request

    Returns:
        dict: Success message
    """
    try:
        payload = decode_access_token(request.token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    # Update the user's password
    user.hashed_password = hash_password(request.new_password)
    # Save the changes to the database
    # Replace with your actual database logic
    print(f"  [AgentName] Password reset successful for {user.username}...")
    return {"message": "Password reset successfully"}


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username and password.

    Args:
        form_data: Login form data

    Returns:
        Token: Access token
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """
    Get the current user.

    Args:
        current_user: Current user

    Returns:
        User: Current user
    """
    return current_user

@router.post("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """
    Refresh the access token.

    Args:
        token: Access token

    Returns:
        Token: New access token
    """
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password_endpoint(request: PasswordResetRequest):
    """
    Send a password reset email to the user.

    Args:
        request: Password reset request

    Returns:
        dict: Success message
    """
    return await forgot_password(request)

@router.post("/reset-password")
async def reset_password_endpoint(request: PasswordReset):
    """
    Reset the user's password with the provided token.

    Args:
        request: Password reset request

    Returns:
        dict: Success message
    """
    return await reset_password(request)