"""
Authentication & Security Module for Sentinel AI
Handles JWT tokens, password hashing, sessions, and role-based access
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os

# ============= SECURITY CONFIG =============
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production-minimum-32-chars")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============= MODELS =============
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: Optional[list] = None

# ============= PASSWORD HASHING =============
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

# ============= JWT TOKEN GENERATION =============
def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> tuple[str, datetime]:
    """
    Create JWT access token
    Returns: (token, expiration_datetime)
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt, expire

def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify JWT token and extract data
    Returns: TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        roles: list = payload.get("roles", [])
        
        if username is None:
            return None
        
        return TokenData(username=username, roles=roles)
    except JWTError:
        return None

# ============= SESSION MANAGEMENT =============
class LoginHistory(BaseModel):
    user_id: int
    username: str
    login_time: datetime
    logout_time: Optional[datetime] = None
    ip_address: str
    status: str  # "Success", "Failed", "Expired"
    reason: Optional[str] = None

def log_login_attempt(
    db: Session,
    username: str,
    ip_address: str,
    status: str,
    reason: Optional[str] = None
):
    """Log login attempt to database"""
    from models import LoginHistoryDB
    
    login_record = LoginHistoryDB(
        username=username,
        login_time=datetime.utcnow(),
        ip_address=ip_address,
        status=status,
        reason=reason
    )
    db.add(login_record)
    db.commit()

def log_logout(db: Session, username: str):
    """Log logout time"""
    from models import LoginHistoryDB
    
    # Get last login record for this user
    last_login = db.query(LoginHistoryDB).filter(
        LoginHistoryDB.username == username,
        LoginHistoryDB.logout_time == None
    ).order_by(LoginHistoryDB.login_time.desc()).first()
    
    if last_login:
        last_login.logout_time = datetime.utcnow()
        db.commit()

# ============= ROLE-BASED ACCESS CONTROL =============
def has_role(token_data: TokenData, required_role: str) -> bool:
    """Check if user has required role"""
    if not token_data or not token_data.roles:
        return False
    return required_role in token_data.roles

def is_admin(token_data: TokenData) -> bool:
    """Check if user is admin"""
    return has_role(token_data, "Admin")

def is_analyst(token_data: TokenData) -> bool:
    """Check if user is analyst"""
    return has_role(token_data, "Analyst") or is_admin(token_data)
