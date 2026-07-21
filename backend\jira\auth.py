"""
backend/jira/auth.py
─────────────────────────────────────────────
Jira Authentication Module
Handles secure authentication with the Jira REST API
using Basic Auth (email + API token via .env).
"""

import os
import base64
import requests
from dotenv import load_dotenv

# ─── Load environment variables from .env ───
load_dotenv()


# ─────────────────────────────────────────────
# Configuration Loader
# ─────────────────────────────────────────────

def get_jira_config() -> dict:
    """
    Loads and validates all required Jira config from .env.
    Raises EnvironmentError if any required key is missing.
    """
    config = {
        "base_url": os.getenv("JIRA_BASE_URL", "").rstrip("/"),
        "email":    os.getenv("JIRA_EMAIL", ""),
        "api_key":  os.getenv("JIRA_API_KEY", ""),
        "project":  os.getenv("JIRA_PROJECT_KEY", ""),
    }

    # Validate required fields
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required Jira environment variables: {missing}\n"
            "Please fill them in your .env file."
        )

    return config


# ─────────────────────────────────────────────
# Auth Header Builder
# ─────────────────────────────────────────────

def get_auth_headers() -> dict:
    """
    Builds Basic Auth headers for Jira REST API v3.
    Encodes email:api_token in Base64 as required by Atlassian.

    Returns:
        dict: HTTP headers with Authorization and Content-Type
    """
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_KEY")
    auth_string = f"{email}:{api_token}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json",
    }
    return headers