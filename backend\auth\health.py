"""
backend/auth/health.py
─────────────────────────────────────────────
API Health Check Module
Handles API status checks.
"""

def get_api_status() -> str:
    """
    Returns the API status.
    """
    return "OK"