"""
backend/auth/auth_routes.py
---------------------------------------------
Authentication Routes - Login & Token Management
Provides secure login and token endpoints.

Endpoints:
  POST /auth/login - Login with username/password
  GET /auth/me - Get current user info
  POST /auth/refresh - Refresh access token
  GET /healthcheck - Check API status
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
    """Get current user from token."""
    user = get_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ─────────────────────────────────────────────
# Dependency: Get Super User
# ─────────────────────────────────────────────

async def get_superuser():
    """Get superuser."""
    # Implement superuser logic here
    pass


# ─────────────────────────────────────────────
# Health Check Endpoint
# ─────────────────────────────────────────────

async def healthcheck():
    """Check API status."""
    # Implement health check logic here
    return {"status": "OK"}


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username/password."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user


@router.post("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """Refresh access token."""
    # Implement refresh token logic here
    pass


@router.get("/healthcheck")
async def healthcheck_endpoint():
    """Check API status."""
    return await healthcheck()