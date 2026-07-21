"""
backend/auth/auth_routes.py
---------------------------------------------
Authentication Routes - Login & Token Management
Provides secure login and token endpoints.

Endpoints:
  POST /auth/login - Login with username/password
  GET /auth/me - Get current user info
  POST /auth/refresh - Refresh access token
  GET /health - Health check endpoint
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List, Dict
from backend.auth.auth import Auth
from backend.auth.health import HealthCheck

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username/password"""
    auth = Auth()
    return await auth.login(form_data.username, form_data.password)

@router.get("/me")
async def get_user_info():
    """Get current user info"""
    auth = Auth()
    return await auth.get_user_info()

@router.post("/refresh")
async def refresh_token():
    """Refresh access token"""
    auth = Auth()
    return await auth.refresh_token()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    health = HealthCheck()
    return await health.check()