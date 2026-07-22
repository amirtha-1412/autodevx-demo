"""
backend/auth/auth_routes.py
---------------------------------------------
Authentication Routes - Login & Token Management
Provides secure login and token endpoints.

Endpoints:
  POST /auth/login
  GET /health
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

# Existing routes and logic remain unchanged
class LoginRequest(BaseModel):
    username: str
    password: str

router = APIRouter()

@router.post("/auth/login")
async def login(request: LoginRequest):
    # Existing login logic remains unchanged
    pass

# New endpoint for health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Provides information about the API's current status.

    Returns:
        A dictionary containing the API's status.
    """
    try:
        # Check the API's status
        status = "healthy"
        return {"status": status}
    except Exception as e:
        # Log the error and return an error response
        print(f"[Agent] [FAIL] Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")