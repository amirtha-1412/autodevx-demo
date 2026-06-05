"""
backend/db/database.py
---------------------------------------------
Database Utilities - User Management
Provides secure user management functionality.

Features:
  - User registration and login
  - User password reset
  - User data retrieval
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# Database Configuration
DB_URL = os.getenv("DB_URL", "sqlite:///database.db")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Create database engine
engine = create_engine(DB_URL)

# Create database session maker
Session = sessionmaker(bind=engine)

# Create database base
Base = declarative_base()


# ─────────────────────────────────────────────
# User Model
# ─────────────────────────────────────────────

class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def __init__(self, username: str, email: str, hashed_password: str):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password


# ─────────────────────────────────────────────
# Dependency: Get Database Session
# ─────────────────────────────────────────────

def get_db():
    """Get database session."""
    db = Session()
    try:
        yield db
    finally:
        db.close()