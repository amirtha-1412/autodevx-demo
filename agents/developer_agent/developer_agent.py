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
import re
from passlib.context import CryptContext

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
        return {
            'success': self.success,
            'generated_files': self.generated_files,
            'code_diff': self.code_diff,
            'implementation_notes': self.implementation_notes,
            'error': self.error
        }

# ─────────────────────────────────────────────
# Email Validation
# ─────────────────────────────────────────────

def validate_email(email: str) -> bool:
    """
    Validate email format using regular expression.

    Args:
        email (str): Email address to validate.

    Returns:
        bool: True if email is valid, False otherwise.
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_regex, email))

# ─────────────────────────────────────────────
# Password Hashing
# ─────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password (str): Password to hash.

    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hashed password.

    Args:
        plain_password (str): Password to verify.
        hashed_password (str): Hashed password to compare.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)