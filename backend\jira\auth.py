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

    Returns:
    - dict: The Jira configuration.
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
    - dict: The authentication headers.
    """
    config = get_jira_config()
    auth = f"{config['email']}:{config['api_key']}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(auth.encode()).decode()}",
        "Content-Type": "application/json"
    }
    return headers


# ─────────────────────────────────────────────
# Jira API Client
# ─────────────────────────────────────────────

class JiraClient:
    """
    Jira API client.
    """

    def __init__(self):
        self.config = get_jira_config()
        self.headers = get_auth_headers()

    def get(self, endpoint: str, params: dict = None):
        """
        Send a GET request to the Jira API.

        Args:
        - endpoint (str): The API endpoint.
        - params (dict): The query parameters.

        Returns:
        - dict: The response data.
        """
        try:
            response = requests.get(
                f"{self.config['base_url']}{endpoint}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  [Jira] Error: {e}")
            raise

    def post(self, endpoint: str, data: dict):
        """
        Send a POST request to the Jira API.

        Args:
        - endpoint (str): The API endpoint.
        - data (dict): The request data.

        Returns:
        - dict: The response data.
        """
        try:
            response = requests.post(
                f"{self.config['base_url']}{endpoint}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  [Jira] Error: {e}")
            raise