"""JWT token handling for authentication"""

import os
import logging
from jose import jwt, JWTError
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def _secret_key() -> str:
    key = (
        os.getenv("SECRET_KEY")
        or os.getenv("JWT_SECRET_KEY")
        or os.getenv("SENTINEL_SECRET_KEY")
    )
    if not key or len(key) < 32 or key.lower().startswith(("your-", "change-me", "replace-me")):
        raise RuntimeError("Configure SECRET_KEY with a random value of at least 32 characters")
    return key


ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def create_access_token(data: dict) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary with token claims
        
    Returns:
        Encoded JWT token
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        encoded_jwt = jwt.encode(
            to_encode,
            _secret_key(),
            algorithm=ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {str(e)}")
        raise


def verify_access_token(token: str) -> dict:
    """
    Verify and decode JWT access token
    
    Args:
        token: JWT token to verify
        
    Returns:
        Token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            _secret_key(),
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None
