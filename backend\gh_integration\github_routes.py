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

router = APIRouter(prefix="/github", tags=["GitHub"])


# ─────────────────────────────────────────────
# Request Models
# ─────────────────────────────────────────────

class CreatePRRequest(BaseModel):
    title: str
    body: str
    head_branch: str
    base_branch: str = "main"
    labels: Optional[List[str]] = None
    reviewers: Optional[List[str]] = None


class CreateBranchRequest(BaseModel):
    branch_name: str
    from_branch: str = "main"


class CommitFilesRequest(BaseModel):
    branch_name: str
    files: Dict[str, str]  # {file_path: content}
    commit_message: str


class CreatePRWithCodeRequest(BaseModel):
    """
    Complete PR creation: branch + commit + PR
    """
    ticket_id: str
    pr_title: str
    pr_body: str
    generated_code: Dict[str, str]  # {file_path: content}
    base_branch: str = "main"
    labels: Optional[List[str]] = None
    reviewers: Optional[List[str]] = None


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@router.get("/status")
async def github_status():
    """Check GitHub integration status."""
    client = GitHubClient()
    
    if client.is_configured():
        return {"status": "OK"}
    else:
        return {"status": "Failed to connect to GitHub"}


@router.get("/healthcheck")
async def healthcheck_endpoint():
    """Check API status."""
    # Implement health check logic here
    return {"status": "OK"}