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
        return {"status": "ok"}
    else:
        return {"status": "not configured"}


@router.post("/create-pr")
async def create_pr(request: CreatePRRequest):
    """Create a new pull request."""
    client = GitHubClient()
    try:
        pr = client.create_pr(
            title=request.title,
            body=request.body,
            head_branch=request.head_branch,
            base_branch=request.base_branch,
            labels=request.labels,
            reviewers=request.reviewers
        )
        return {"pr": pr}
    except Exception as e:
        print(f"  [GitHub] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pull request"
        )


@router.post("/create-branch")
async def create_branch(request: CreateBranchRequest):
    """Create a new branch."""
    client = GitHubClient()
    try:
        branch = client.create_branch(
            branch_name=request.branch_name,
            from_branch=request.from_branch
        )
        return {"branch": branch}
    except Exception as e:
        print(f"  [GitHub] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create branch"
        )


@router.post("/commit-files")
async def commit_files(request: CommitFilesRequest):
    """Commit files to a branch."""
    client = GitHubClient()
    try:
        commit = client.commit_files(
            branch_name=request.branch_name,
            files=request.files,
            commit_message=request.commit_message
        )
        return {"commit": commit}
    except Exception as e:
        print(f"  [GitHub] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to commit files"
        )


@router.post("/create-pr-with-code")
async def create_pr_with_code(request: CreatePRWithCodeRequest):
    """Create a new pull request with generated code."""
    client = GitHubClient()
    try:
        pr = client.create_pr_with_code(
            ticket_id=request.ticket_id,
            pr_title=request.pr_title,
            pr_body=request.pr_body,
            generated_code=request.generated_code,
            base_branch=request.base_branch,
            labels=request.labels,
            reviewers=request.reviewers
        )
        return {"pr": pr}
    except Exception as e:
        print(f"  [GitHub] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pull request with code"
        )