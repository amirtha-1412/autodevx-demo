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
    config = get_jira_config()

    # Encode credentials: email:api_token → base64
    credentials = f"{config['email']}:{config['api_key']}"
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json"
    }


# ─────────────────────────────────────────────
# Jira Connection Tester
# ─────────────────────────────────────────────

def test_jira_connection() -> dict:
    """
    Tests the Jira connection by calling /rest/api/3/myself.
    Returns the authenticated user's profile on success.

    Returns:
        dict: { "success": bool, "user": str, "account_id": str, "error": str }
    """
    try:
        config  = get_jira_config()
        headers = get_auth_headers()

        url      = f"{config['base_url']}/rest/api/3/myself"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return {"success": True, "user": response.json()["name"], "account_id": response.json()["accountId"], "error": ""}
        else:
            return {"success": False, "user": "", "account_id": "", "error": response.text}
    except Exception as e:
        return {"success": False, "user": "", "account_id": "", "error": str(e)}