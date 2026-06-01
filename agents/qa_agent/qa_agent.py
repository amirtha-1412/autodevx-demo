"""
agents/qa_agent/qa_agent.py
---------------------------------------------
QA Agent - Real Test Generation & Validation
Generates test cases and validates code quality.

Features:
  - LLM-powered test generation
  - Generates actual pytest test files
  - Executes pytest and captures results
  - Code quality analysis
  - Security vulnerability detection
  - Test case validation
  - Detailed feedback for developers
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from agents.llm import call_llm
import subprocess
import os
import tempfile
import shutil
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from agents.database import get_db
from agents.user import get_current_active_user

# ─────────────────────────────────────────────
# QA Result
# ─────────────────────────────────────────────

@dataclass
class QAResult:
    """Result of QA validation."""
    success: bool
    test_status: str  # PASSED, FAILED, PARTIAL
    test_cases: List[str] = field(default_factory=list)
    test_results: Dict[str, str] = field(default_factory=dict)  # {test: status}
    test_files: 
    implementation_notes: str = ""
    error: str = ""

# ─────────────────────────────────────────────
# User Authentication
# ─────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(UserInDB).filter(UserInDB.username == username).first()

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "secret_key", algorithm="HS256")
    return encoded_jwt

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ─────────────────────────────────────────────
# Role-Based Access Control (RBAC)
# ─────────────────────────────────────────────

class Role(BaseModel):
    name: str

class UserRoles(BaseModel):
    user_id: int
    role_id: int

class RoleInDB(Role):
    id: int

class UserInDB(User):
    roles: List[RoleInDB]

def get_user_roles(db: Session, user_id: int):
    return db.query(UserInDB).filter(UserInDB.id == user_id).first()

def authenticate_user_role(fake_db, username: str, role: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if role not in [r.name for r in user.roles]:
        return False
    return user

# ─────────────────────────────────────────────
# Endpoint Protection
# ─────────