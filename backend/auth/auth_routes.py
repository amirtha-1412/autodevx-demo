"""
backend/auth/auth_routes.py
---------------------------------------------
Authentication Routes - Login & Token Management
Provides secure login and token endpoints.

Endpoints:
  POST /auth/login - Login with username/password
  GET /auth/me - Get current user info
  POST /auth/refresh - Refresh access token
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
)
from backend.jira.auth import get_jira_config, get_auth_headers

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


# ─────────────────────────────────────────────
# OAuth2 Configuration
# ─────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ─────────────────────────────────────────────
# Dependency: Get Current User
# ─────────────────────────────────────────────

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user based on the access token."""
    try:
        payload = decode_access_token(token)
        user = get_user(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ─────────────────────────────────────────────
# Dependency: Get Current Active User
# ─────────────────────────────────────────────

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get the current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ─────────────────────────────────────────────
# Login Endpoint
# ─────────────────────────────────────────────

async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username/password and get access token."""
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


# ─────────────────────────────────────────────
# Get User Info Endpoint
# ─────────────────────────────────────────────

async def get_user_info(current_user: User = Depends(get_current_active_user)):
    """Get the current user's info."""
    jira_config = get_jira_config()
    auth_headers = get_auth_headers()
    response = requests.get(
        f"{jira_config['base_url']}/rest/api/3/myself", headers=auth_headers
    )
    response.raise_for_status()
    user_info = response.json()
    return user_info


# ─────────────────────────────────────────────
# Refresh Token Endpoint
# ─────────────────────────────────────────────

async def refresh_token(token: str = Depends(oauth2_scheme)):
    """Refresh the access token."""
    try:
        payload = decode_access_token(token)
        user = get_user(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}