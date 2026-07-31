"""
backend/auth/auth_routes.py
---------------------------------------------
Authentication Routes - Login & Token Management
Provides secure login and token endpoints.

Endpoints:
  POST /auth/login
  GET /auth/health
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
import logging

# Create a logger
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

# Define a response model for the health check endpoint
class HealthCheckResponse(BaseModel):
    """Response model for the health check endpoint"""
    status: str
    message: str

@router.get("/auth/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        A dictionary containing the status and message of the API.
    """
    try:
        # Check the API's status
        status = "OK"
        message = "The API is running normally."
        logger.info("  [Agent] Health check: OK")
        return {"status": status, "message": message}
    except Exception as e:
        # Handle any exceptions
        status = "FAIL"
        message = "An error occurred during the health check."
        logger.error(f"  [Agent] Health check: {str(e)}")
        return {"status": status, "message": message}

# Existing routes...