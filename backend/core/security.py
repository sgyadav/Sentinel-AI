"""Security utilities and dependency injection"""

import logging
import hmac
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from auth.jwt_handler import verify_access_token
from database import get_db
from models import UserDB

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)
agent_security = HTTPBearer(auto_error=False, scheme_name="AgentBearer")


def refresh_user_claims(payload: dict, db: Session) -> Optional[dict]:
    """Return claims only while the account and its token version remain valid."""
    username = payload.get("sub")
    if not username:
        return None
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user or not user.is_active:
        return None
    try:
        if int(payload.get("ver", 0)) != int(user.token_version or 0):
            return None
    except (TypeError, ValueError):
        return None
    payload["role"] = user.role
    return payload


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Token payload with user info
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    current_payload = refresh_user_claims(payload, db)
    if not current_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or revoked user token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_payload


async def get_current_agent(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(agent_security),
) -> bool:
    """Validate the shared, high-entropy credential used by endpoint agents."""
    expected_token = os.getenv("SENTINEL_AGENT_TOKEN", "")
    if len(expected_token) < 32:
        logger.error("SENTINEL_AGENT_TOKEN is missing or shorter than 32 characters")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent authentication is not configured",
        )
    if not credentials or not hmac.compare_digest(credentials.credentials, expected_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Get current user and verify admin role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User payload if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") not in ["Admin", "SuperAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - Admin role required"
        )
    
    return current_user
