"""JWT token handling for authentication"""

import os
import logging
from jose import jwt, JWTError
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-minimum-32-chars")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Warn if using default secret key
if SECRET_KEY == "your-secret-key-change-in-production-minimum-32-chars":
    logger.warning("⚠️  Using default SECRET_KEY - CHANGE THIS IN PRODUCTION!")


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
            SECRET_KEY,
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
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None