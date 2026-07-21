from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.jira.auth import authenticate_jira

router = APIRouter()

class HealthCheck(BaseModel):
    status: str

@router.get("/healthcheck")
def healthcheck():
    try:
        # Authenticate Jira
        jira_user = authenticate_jira()
        
        # Return API status
        return HealthCheck(status="OK")
    except Exception as e:
        # Log error and return error status
        print(f"[FAIL] Healthcheck failed: {e}")
        return HealthCheck(status="ERROR")

# Add healthcheck endpoint to router
router.add_api_route("/healthcheck", healthcheck, methods=["GET"])

# Return router
return router