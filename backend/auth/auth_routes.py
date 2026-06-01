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
from backend.jira.auth import get_jira_config, get_auth_headers, test_jira_connection
from backend.gh_integration.github_routes import GitHubClient

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
    """Get the current user from the access token."""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        user = get_user(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


# ─────────────────────────────────────────────
# Dependency: Get Current Active User
# ─────────────────────────────────────────────

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get the current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return current_user


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

router = APIRouter(prefix="/api", tags=["Auth"])


@router.post("/auth/login")
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


@router.get("/auth/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get the current user's profile information."""
    try:
        config = get_jira_config()
        headers = get_auth_headers()
        url = f"{config['base_url']}/rest/api/3/myself"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/refresh")
async def refresh_access_token(token: str = Depends(oauth2_scheme)):
    """Refresh access token."""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        user = get_user(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))