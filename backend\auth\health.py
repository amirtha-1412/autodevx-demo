"""
backend/auth/health.py
─────────────────────────────────────────────
Health Check Module
Provides a health check endpoint to verify API status.
"""

def get_health_status() -> dict:
    """
    Returns a dictionary with API status information.
    """
    return {"status": "OK", "message": "API is running"}