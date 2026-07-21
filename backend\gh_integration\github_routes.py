"""
backend/github/github_routes.py
---------------------------------------------
GitHub API Routes
REST endpoints for GitHub integration.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from backend.gh_integration.github_client import GitHubClient
from backend.auth.health import HealthCheck

router = APIRouter(prefix="/github", tags=["GitHub"])

# ───────────────────
# GitHub API Routes
# ───────────────────

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    health = HealthCheck()
    return await health.check()