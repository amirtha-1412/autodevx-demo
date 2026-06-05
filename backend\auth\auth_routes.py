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
  POST /auth/reset-password - Reset password
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
    generate_password_reset_token,
    validate_password_reset_token,
)
from backend.auth.email_utils import send_password_reset_email

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
    """Get the current user from the token."""
    try:
        payload = decode_access_token(token)
        user = get_user(payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─────────────────────────────────────────────
# Forgot Password Endpoint
# ─────────────────────────────────────────────

async def forgot_password(request: PasswordResetRequest):
    """Send a password reset email to the user."""
    user = get_user(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    token = generate_password_reset_token(user)
    send_password_reset_email(user.email, token)
    return {"message": "Password reset email sent"}


# ─────────────────────────────────────────────
# Reset Password Endpoint
# ─────────────────────────────────────────────

async def reset_password(request: PasswordReset):
    """Reset the user's password."""
    user = validate_password_reset_token(request.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user.hashed_password = hash_password(request.new_password)
    # Update the user in the database
    return {"message": "Password reset successfully"}


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

router = APIRouter()

@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username and password."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the current user."""
    return current_user

@router.post("/auth/refresh")
async def refresh_access_token(token: str = Depends(oauth2_scheme)):
    """Refresh the access token."""
    try:
        payload = decode_access_token(token)
        user = get_user(payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/auth/forgot-password")
async def forgot_password_endpoint(request: PasswordResetRequest):
    """Send a password reset email to the user."""
    return await forgot_password(request)

@router.post("/auth/reset-password")
async def reset_password_endpoint(request: PasswordReset):
    """Reset the user's password."""
    return await reset_password(request)