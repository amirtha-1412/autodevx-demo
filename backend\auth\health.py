"""
backend/auth/health.py
─────────────────────────────────────────────
Health Check Module
Provides a health check endpoint.
"""

class HealthCheck:
    async def check(self):
        return {"status": "OK"}