import os
from pydantic import BaseModel
from requests import get

class JiraAuth(BaseModel):
    email: str
    api_token: str

def authenticate_jira():
    try:
        # Load Jira credentials from .env
        jira_email = os.environ["JIRA_EMAIL"]
        jira_api_token = os.environ["JIRA_API_TOKEN"]
        
        # Authenticate Jira
        response = get("https://your-jira-instance.atlassian.net/rest/api/2/user", 
                       auth=(jira_email, jira_api_token))
        
        # Return authenticated user
        return response.json()["name"]
    except Exception as e:
        # Log error and raise exception
        print(f"[FAIL] Jira authentication failed: {e}")
        raise e