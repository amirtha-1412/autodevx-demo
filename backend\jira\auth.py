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

class Auth:
    def __init__(self):
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")

    async def login(self, username, password):
        # Implement login logic here
        pass

    async def get_user_info(self):
        # Implement get user info logic here
        pass

    async def refresh_token(self):
        # Implement refresh token logic here
        pass