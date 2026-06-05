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
from fastapi import HTTPException, status

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
    jira_config = get_jira_config()
    auth = f"{jira_config['email']}:{jira_config['api_key']}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(auth.encode()).decode()}",
        "Content-Type": "application/json"
    }
    return headers


# ─────────────────────────────────────────────
# Send Email
# ─────────────────────────────────────────────

def send_email(to: str, subject: str, body: str):
    """
    Send an email using Jira's email service.

    Args:
        to: Recipient's email
        subject: Email subject
        body: Email body

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Send email using Jira's email service
        # Replace with your actual email sending logic
        print(f"  [AgentName] Sending email to {to}...")
        return True
    except Exception as e:
        print(f"  [AgentName] Failed to send email: {e}")
        return False