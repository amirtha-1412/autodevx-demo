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
from fastapi.responses import JSONResponse
from backend.auth.auth_utils import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from backend.email import send_email
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.models import User
import uuid

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


class PasswordResetRequest(BaseModel):
    """Password reset request model."""
    email: str


class PasswordReset(BaseModel):
    """Password reset model."""
    token: str
    new_password: str


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────----

router = APIRouter(tags=["auth"])


@router.post("/auth/forgot-password")
async def forgot_password(password_reset_request: PasswordResetRequest):
    """
    Send password reset email to the user's registered email address.

    Args:
    - password_reset_request (PasswordResetRequest): The password reset request.

    Returns:
    - JSONResponse: A JSON response indicating whether the email was sent successfully.
    """
    db = get_db()
    user = db.query(User).filter(User.email == password_reset_request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    token = str(uuid.uuid4())
    user.password_reset_token = token
    db.commit()

    send_email(
        recipient=user.email,
        subject="Password Reset",
        body=f"Reset your password: {token}",
    )

    return JSONResponse(content={"message": "Password reset email sent"}, status_code=status.HTTP_200_OK)


@router.post("/auth/reset-password")
async def reset_password(password_reset: PasswordReset):
    """
    Reset password with token.

    Args:
    - password_reset (PasswordReset): The password reset request.

    Returns:
    - JSONResponse: A JSON response indicating whether the password was reset successfully.
    """
    db = get_db()
    user = db.query(User).filter(User.password_reset_token == password_reset.token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token")

    user.password = password_reset.new_password
    user.password_reset_token = None
    db.commit()

    return JSONResponse(content={"message": "Password reset successfully"}, status_code=status.HTTP_200_OK)