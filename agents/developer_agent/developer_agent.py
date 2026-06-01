"""
agents/developer_agent/developer_agent.py
---------------------------------------------
Developer Agent - Intelligent Code Modification
Generates production-ready code based on requirements.

Features:
  - LLM-powered code generation
  - Repository-aware file modification
  - Semantic code understanding
  - Context-aware synthesis
  - Multiple file support
  - Diff generation
  - Retry with QA feedback
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from agents.llm import call_llm
from agents.developer_agent.repository_analyzer import RepositoryAnalyzer
from typing import Dict, List, Optional
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
# Code Generation Result
# ─────────────────────────────────────────────

@dataclass
class CodeGenerationResult:
    """Result of code generation."""
    success: bool
    generated_files: Dict[str, str] = field(default_factory=dict)  # {filename: code}
    code_diff: str = ""
    implementation_notes: str = ""
    error: str = ""
    
    def to_dict(self):
        return self.__dict__

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
# ─────────────────────────────────────────────

def protect_endpoint(endpoint: str, allowed_roles: List[str]):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = await get_current_active_user()
            if current_user.username not in [r.name for r in current_user.roles] and endpoint not in allowed_roles:
                raise HTTPException(status_code=403, detail="Forbidden")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Example usage:
@app.get("/protected_endpoint")
@protect_endpoint("/protected_endpoint", ["admin"])
async def protected_endpoint():
    return {"message": "Hello, admin!"}